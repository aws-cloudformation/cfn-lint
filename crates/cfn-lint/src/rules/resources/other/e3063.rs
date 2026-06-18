use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3063: Validate GuardDuty Detector property exclusivity.
///
/// Both DataSources and Features cannot be provided together.
pub struct E3063;

impl CfnLintRule for E3063 {
    fn id(&self) -> &str { "E3063" }
    fn short_description(&self) -> &str {
        "Validate GuardDuty Detector property exclusivity"
    }
    fn description(&self) -> &str {
        "Both DataSources and Features cannot be provided. Use Features instead."
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::GuardDuty::Detector/Properties"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let props = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        if props.get("DataSources").is_some() && props.get("Features").is_some() {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "Both 'DataSources' and 'Features' were provided. You can provide only one; it is recommended to use 'Features'.".to_string(),
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
    fn test_features_only_ok() {
        let yaml = br#"
Resources:
  Detector:
    Type: AWS::GuardDuty::Detector
    Properties:
      Enable: true
      Features:
        - Name: S3_DATA_EVENTS
          Status: ENABLED
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Detector").unwrap()
            .get("Properties").unwrap();
        let path = vec!["Resources".to_string(), "Detector".to_string(), "Properties".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3063.validate(&validator, "Resources/AWS::GuardDuty::Detector/Properties", instance, &serde_json::json!({}), &path);
        assert!(errors.is_empty());
    }

    #[test]
    fn test_both_datasources_and_features() {
        let yaml = br#"
Resources:
  Detector:
    Type: AWS::GuardDuty::Detector
    Properties:
      Enable: true
      DataSources:
        S3Logs:
          Enable: true
      Features:
        - Name: S3_DATA_EVENTS
          Status: ENABLED
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Detector").unwrap()
            .get("Properties").unwrap();
        let path = vec!["Resources".to_string(), "Detector".to_string(), "Properties".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3063.validate(&validator, "Resources/AWS::GuardDuty::Detector/Properties", instance, &serde_json::json!({}), &path);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("DataSources"));
        assert!(errors[0].message.contains("Features"));
    }
}

crate::register_cfn_lint_rule!(E3063);
