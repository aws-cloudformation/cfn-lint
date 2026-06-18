use crate::ast::{AstNode, FunctionNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3015: Validate the resource condition is valid.
///
/// Dynamically builds a schema with the condition names from the template
/// and validates that each resource's Condition references an existing condition.
pub struct E3015;

impl CfnLintRule for E3015 {
    fn id(&self) -> &str { "E3015" }
    fn short_description(&self) -> &str { "Validate the resource condition is valid" }
    fn description(&self) -> &str {
        "Validates resource Condition references exist in Conditions section"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/Condition"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        if !matches!(instance, AstNode::String(_)) {
            return vec![];
        }

        let condition_names: Vec<serde_json::Value> = if let Some(ctx) = validator.context() {
            ctx.template
                .conditions
                .keys()
                .map(|k| serde_json::Value::String(k.clone()))
                .collect()
        } else {
            // Without context, cannot validate condition names
            return vec![];
        };

        // If no conditions are defined, any condition reference is invalid.
        let schema = if condition_names.is_empty() {
            serde_json::json!({"type": "string", "enum": []})
        } else {
            serde_json::json!({"type": "string", "enum": condition_names})
        };

        let schema_validator = crate::jsonschema::Validator::new(schema.clone());
        schema_validator
            .validate(instance, &schema, path)
            .into_iter()
            .filter(|err| err.keyword == "type" || err.keyword == "enum")
            .map(|mut err| {
                err.keyword = format!("cfnLint:{}", self.id());
                err
            })
            .collect()
    }
}

crate::register_cfn_lint_rule!(E3015);

/// Extract the (resource_name, attribute) pair from a GetAtt function node.
pub fn parse_getatt_args(func: &FunctionNode) -> Option<(String, String)> {
    match func.args.as_ref() {
        AstNode::Array(arr) if arr.elements.len() == 2 => {
            let resource = arr.elements[0].as_str()?;
            let attr = arr.elements[1].as_str()?;
            Some((resource.to_string(), attr.to_string()))
        }
        AstNode::String(s) => {
            let dot_pos = s.value.find('.')?;
            let resource = &s.value[..dot_pos];
            let attr = &s.value[dot_pos + 1..];
            if resource.is_empty() || attr.is_empty() {
                return None;
            }
            Some((resource.to_string(), attr.to_string()))
        }
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_valid_condition_ref() {
        let yaml = br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref AWS::Region
      - us-east-1
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Condition: IsProd
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Bucket").unwrap()
            .get("Condition").unwrap();
        let path = vec!["Resources".to_string(), "Bucket".to_string(), "Condition".to_string()];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(serde_json::json!({}), std::sync::Arc::new(ctx));
        let errors = E3015.validate(&validator, "Resources/*/Condition", instance, &serde_json::json!({}), &path);
        assert!(errors.is_empty());
    }

    #[test]
    fn test_undefined_condition() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Condition: DoesNotExist
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Bucket").unwrap()
            .get("Condition").unwrap();
        let path = vec!["Resources".to_string(), "Bucket".to_string(), "Condition".to_string()];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(serde_json::json!({}), std::sync::Arc::new(ctx));
        let errors = E3015.validate(&validator, "Resources/*/Condition", instance, &serde_json::json!({}), &path);
        assert!(!errors.is_empty());
    }

    #[test]
    fn test_no_condition_no_issue() {
        // This test is now irrelevant since validate() only fires when Condition is present.
        // The keyword dispatch ensures we only get called on Resources/*/Condition nodes.
    }

    #[test]
    fn test_parse_getatt_array_form() {
        let func = FunctionNode {
            name: "Fn::GetAtt".to_string(),
            args: Box::new(AstNode::Array(ArrayNode {
                elements: vec![
                    AstNode::String(StringNode { value: "MyBucket".to_string(), span: Span::default() }),
                    AstNode::String(StringNode { value: "Arn".to_string(), span: Span::default() }),
                ],
                span: Span::default(),
            })),
            span: Span::default(),
        };
        let (res, attr) = parse_getatt_args(&func).unwrap();
        assert_eq!(res, "MyBucket");
        assert_eq!(attr, "Arn");
    }

    #[test]
    fn test_parse_getatt_string_form() {
        let func = FunctionNode {
            name: "Fn::GetAtt".to_string(),
            args: Box::new(AstNode::String(StringNode {
                value: "MyBucket.Arn".to_string(),
                span: Span::default(),
            })),
            span: Span::default(),
        };
        let (res, attr) = parse_getatt_args(&func).unwrap();
        assert_eq!(res, "MyBucket");
        assert_eq!(attr, "Arn");
    }
}
