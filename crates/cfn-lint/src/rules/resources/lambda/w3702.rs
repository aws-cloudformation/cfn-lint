use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W3702: Lambda layer ARN using 'awslayer' format may not be available
pub struct W3702;

impl CfnLintRule for W3702 {
    fn id(&self) -> &str {
        "W3702"
    }
    fn short_description(&self) -> &str {
        "awslayer ARN format may not be available"
    }
    fn description(&self) -> &str {
        "Layer ARNs using the 'awslayer' format may not be available."
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Lambda::Function/Properties/Layers/*"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let val = match instance.as_str() {
            Some(v) => v,
            None => return vec![],
        };

        if val.starts_with("arn:") && val.contains(":lambda:::awslayer:") {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} uses the 'awslayer' format which may not be available",
                    val
                ),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_awslayer_flagged() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Layers:
        - arn:aws:lambda:::awslayer:my-layer
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("Layers")
            .unwrap()
            .as_array()
            .unwrap()
            .elements
            .first()
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "Layers".to_string(),
            "0".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3702.validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties/Layers/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("awslayer"));
    }

    #[test]
    fn test_normal_layer_ok() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Layers:
        - arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("Layers")
            .unwrap()
            .as_array()
            .unwrap()
            .elements
            .first()
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "Layers".to_string(),
            "0".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3702.validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties/Layers/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }
}

crate::register_cfn_lint_rule!(W3702);
