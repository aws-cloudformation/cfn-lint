use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E6005: Validate the Output condition is valid.
///
/// Check the condition of an output to make sure it exists inside the template.
/// Uses the schema engine with an `{"enum": [...]}` schema built from the
/// template's condition names, mirroring the Python implementation.
pub struct E6005;

impl CfnLintRule for E6005 {
    fn id(&self) -> &str {
        "E6005"
    }
    fn short_description(&self) -> &str {
        "Validate the Output condition is valid"
    }
    fn description(&self) -> &str {
        "Check the condition of an output to make sure it exists inside the template"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Outputs/*/Condition"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        // Instance is the condition name node (e.g. a string "IsProd")
        // Only validate string instances
        if instance.as_str().is_none() {
            return vec![];
        }

        // Build enum schema from the template's conditions
        let condition_names: Vec<serde_json::Value> = match validator.context() {
            Some(ctx) => ctx
                .template
                .conditions
                .keys()
                .map(|k| serde_json::Value::String(k.clone()))
                .collect(),
            None => return vec![],
        };

        if condition_names.is_empty() {
            // No conditions defined — any condition name is invalid
            return vec![ValidationError {
                rule_id: None,
                keyword: "enum".to_string(),
                message: format!("'{}' is not one of []", instance.as_str().unwrap_or("")),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        let schema = serde_json::json!({"enum": condition_names});
        let v = validator.without_cfn_lint_rules();
        v.validate_schema(instance, &schema, path)
            .into_iter()
            .filter(|e| !e.unknown)
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::context::Context;
    use crate::jsonschema::Validator;
    use crate::parser;
    use crate::template::Template;
    use std::sync::Arc;

    fn make_validator(yaml: &[u8]) -> (Validator, AstNode) {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Arc::new(Template::from_ast(&ast).unwrap());
        let ctx = Context::new(tmpl);
        let mut v = Validator::new(serde_json::json!({}));
        v.context = Some(Arc::new(ctx));
        (v, ast)
    }

    #[test]
    fn test_valid_output_condition() {
        let yaml = br#"
Conditions:
  IsProd:
    Fn::Equals:
      - a
      - b
Outputs:
  BucketArn:
    Condition: IsProd
    Value: !Ref Bucket
"#;
        let (validator, ast) = make_validator(yaml);
        let cond_node = ast
            .get("Outputs")
            .unwrap()
            .get("BucketArn")
            .unwrap()
            .get("Condition")
            .unwrap();
        let path = vec!["Outputs".into(), "BucketArn".into(), "Condition".into()];
        let errors = E6005.validate(
            &validator,
            "Outputs/*/Condition",
            cond_node,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_invalid_output_condition() {
        let yaml = br#"
Outputs:
  BucketArn:
    Condition: MissingCondition
    Value: !Ref Bucket
"#;
        let (validator, ast) = make_validator(yaml);
        let cond_node = ast
            .get("Outputs")
            .unwrap()
            .get("BucketArn")
            .unwrap()
            .get("Condition")
            .unwrap();
        let path = vec!["Outputs".into(), "BucketArn".into(), "Condition".into()];
        let errors = E6005.validate(
            &validator,
            "Outputs/*/Condition",
            cond_node,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert_eq!(errors[0].keyword, "enum");
    }
}

crate::register_cfn_lint_rule!(E6005);
