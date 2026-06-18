use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W3697: Resource type is from a service in maintenance mode.
///
/// Checks if a resource type belongs to an AWS service that is
/// in maintenance mode with no new features.
pub struct W3697;

impl CfnLintRule for W3697 {
    fn id(&self) -> &str {
        "W3697"
    }
    fn short_description(&self) -> &str {
        "Resource type is from a service in maintenance mode"
    }
    fn description(&self) -> &str {
        "Checks if a resource type belongs to an AWS service that is \
         in maintenance mode with no new features"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let obj = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        let resource_type = match obj.get("Type").and_then(|t| t.as_str()) {
            Some(t) => t,
            None => return vec![],
        };

        if let Some((_, date)) = MAINTENANCE_TYPES.iter().find(|(t, _)| *t == resource_type) {
            let mut props_path = path.to_vec();
            props_path.push("Properties".to_string());

            let span = obj.get("Properties").map(|n| n.span()).unwrap_or_default();

            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "Resource type '{}' is from a service in maintenance mode since {}. \
                     Consider migrating to an alternative",
                    resource_type, date
                ),
                path: props_path,
                span,
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

/// Known maintenance-mode resource types with their maintenance start dates.
const MAINTENANCE_TYPES: &[(&str, &str)] =
    &[("AWS::AutoScaling::LaunchConfiguration", "2024-10-01")];

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(W3697.id(), "W3697");
        assert_eq!(W3697.severity(), Severity::Warning);
        assert!(W3697.description().contains("maintenance"));
    }

    #[test]
    fn test_no_maintenance_resources() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("Bucket").unwrap();
        let path = vec!["Resources".to_string(), "Bucket".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3697.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_maintenance_resource_detected() {
        let yaml = br#"
Resources:
  LC:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      ImageId: ami-12345678
      InstanceType: t2.micro
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("LC").unwrap();
        let path = vec!["Resources".to_string(), "LC".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3697.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0]
            .message
            .contains("AWS::AutoScaling::LaunchConfiguration"));
        assert!(errors[0].message.contains("2024-10-01"));
        assert_eq!(errors[0].path, vec!["Resources", "LC", "Properties"]);
    }

    #[test]
    fn test_mixed_resources() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
  LC:
    Type: AWS::AutoScaling::LaunchConfiguration
    Properties:
      ImageId: ami-12345678
      InstanceType: t2.micro
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("LC").unwrap();
        let path = vec!["Resources".to_string(), "LC".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3697.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("LaunchConfiguration"));
    }
}

crate::register_cfn_lint_rule!(W3697);
