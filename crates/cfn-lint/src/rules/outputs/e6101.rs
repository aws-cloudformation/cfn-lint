use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ContextEvolution, ValidationError, Validator};
use crate::rules::Severity;

/// The set of intrinsic functions allowed in Output Value context.
const OUTPUT_VALUE_FUNCTIONS: &[&str] = &[
    "Fn::Base64",
    "Fn::FindInMap",
    "Fn::GetAtt",
    "Fn::GetAZs",
    "Fn::GetStackOutput",
    "Fn::If",
    "Fn::ImportValue",
    "Fn::Join",
    "Fn::Select",
    "Fn::Split",
    "Fn::Sub",
    "Fn::Transform",
    "Fn::ToJsonString",
    "Fn::Length",
    "Fn::Cidr",
    "Ref",
];

/// E6101: Validate that output values are a string.
///
/// Uses the schema engine with an evolved context that restricts allowed
/// functions and validates against `{"type": ["string"]}`. If the output
/// has a Condition, that condition is pinned to true in the evolved context.
pub struct E6101;

impl CfnLintRule for E6101 {
    fn id(&self) -> &str {
        "E6101"
    }
    fn short_description(&self) -> &str {
        "Validate that outputs values are a string"
    }
    fn description(&self) -> &str {
        "Make sure that output values have a type of string"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Outputs/*"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        // instance is the output object (e.g. {"Value": ..., "Condition": ...})
        let value_node = match instance.get("Value") {
            Some(v) => v,
            None => return vec![],
        };

        // If the output has a Condition, pin it to true in context
        let condition_state = if let Some(cond_node) = instance.get("Condition") {
            if let Some(cond_name) = cond_node.as_str() {
                let mut state = std::collections::HashMap::new();
                state.insert(cond_name.to_string(), true);
                Some(state)
            } else {
                None
            }
        } else {
            None
        };

        // Evolve context: restrict functions, optionally pin condition
        let evolved = validator.evolve(ContextEvolution {
            functions: Some(
                OUTPUT_VALUE_FUNCTIONS
                    .iter()
                    .map(|s| s.to_string())
                    .collect(),
            ),
            condition_state,
            ..Default::default()
        });

        // Validate value through the schema engine with {"type": ["string"]}
        let schema = serde_json::json!({"type": ["string"]});
        let mut value_path = path.to_vec();
        value_path.push("Value".to_string());
        let v = evolved.without_cfn_lint_rules();
        v.validate_schema(value_node, &schema, &value_path)
            .into_iter()
            .filter(|e| !e.unknown)
            .filter(|e| e.keyword != "fn_getatt")
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
    fn test_string_value_passes() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
Outputs:
  Out1:
    Value: my-value
"#;
        let (validator, ast) = make_validator(yaml);
        let output = ast.get("Outputs").unwrap().get("Out1").unwrap();
        let path = vec!["Outputs".into(), "Out1".into()];
        let errors = E6101.validate(
            &validator,
            "Outputs/*",
            output,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_non_string_value_fails() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
Outputs:
  Out1:
    Value:
      - item1
      - item2
"#;
        let (validator, ast) = make_validator(yaml);
        let output = ast.get("Outputs").unwrap().get("Out1").unwrap();
        let path = vec!["Outputs".into(), "Out1".into()];
        let errors = E6101.validate(
            &validator,
            "Outputs/*",
            output,
            &serde_json::json!({}),
            &path,
        );
        assert!(!errors.is_empty());
        assert!(errors.iter().any(|e| e.keyword == "type"));
    }

    #[test]
    fn test_fn_sub_value_allowed() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
Outputs:
  Out1:
    Value: !Sub "${Bucket.Arn}"
"#;
        let (validator, ast) = make_validator(yaml);
        let output = ast.get("Outputs").unwrap().get("Out1").unwrap();
        let path = vec!["Outputs".into(), "Out1".into()];
        let errors = E6101.validate(
            &validator,
            "Outputs/*",
            output,
            &serde_json::json!({}),
            &path,
        );
        assert!(
            errors.is_empty(),
            "Fn::Sub should be allowed in output values"
        );
    }

    #[test]
    fn test_no_value_key_no_error() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
Outputs:
  Out1:
    Description: missing value
"#;
        let (validator, ast) = make_validator(yaml);
        let output = ast.get("Outputs").unwrap().get("Out1").unwrap();
        let path = vec!["Outputs".into(), "Out1".into()];
        let errors = E6101.validate(
            &validator,
            "Outputs/*",
            output,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }
}

crate::register_cfn_lint_rule!(E6101);
