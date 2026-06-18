use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3046: Validate ECS task logging configuration for awslogs.
/// When using 'awslogs' driver, 'awslogs-group' and 'awslogs-region' are required.
pub struct E3046;

impl CfnLintRule for E3046 {
    fn id(&self) -> &str {
        "E3046"
    }
    fn short_description(&self) -> &str {
        "Validate ECS task logging configuration for awslogs"
    }
    fn description(&self) -> &str {
        "When 'awslogs' the options 'awslogs-group' and 'awslogs-region' are required"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions/*/LogConfiguration"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let log_config = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        let driver = match log_config.get("LogDriver").and_then(|n| n.as_str()) {
            Some(d) => d,
            None => return vec![],
        };

        if driver != "awslogs" {
            return vec![];
        }

        let options = log_config.get("Options").and_then(|n| n.as_object());
        let mut errors = Vec::new();

        for required in &["awslogs-group", "awslogs-region"] {
            let has_option = options
                .map(|o| o.contains_key(*required))
                .unwrap_or(false);
            if !has_option {
                let mut options_path = path.to_vec();
                options_path.push("Options".to_string());
                errors.push(ValidationError {
                rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: format!(
                        "When using 'awslogs' log driver, '{}' is required in LogConfiguration Options",
                        required
                    ),
                    path: options_path,
                    span: instance.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
            }
        }

        errors
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_awslogs_with_required_options() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: app
          Image: nginx
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: /ecs/app
              awslogs-region: us-east-1
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Task").unwrap()
            .get("Properties").unwrap()
            .get("ContainerDefinitions").unwrap()
            .as_array().unwrap()
            .elements.first().unwrap()
            .get("LogConfiguration").unwrap();
        let path = vec![
            "Resources".to_string(), "Task".to_string(),
            "Properties".to_string(), "ContainerDefinitions".to_string(),
            "0".to_string(), "LogConfiguration".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3046.validate(&validator, "Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions/*/LogConfiguration", instance, &serde_json::json!({}), &path);
        assert!(errors.is_empty());
    }

    #[test]
    fn test_awslogs_missing_options() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: app
          Image: nginx
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-stream-prefix: ecs
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Task").unwrap()
            .get("Properties").unwrap()
            .get("ContainerDefinitions").unwrap()
            .as_array().unwrap()
            .elements.first().unwrap()
            .get("LogConfiguration").unwrap();
        let path = vec![
            "Resources".to_string(), "Task".to_string(),
            "Properties".to_string(), "ContainerDefinitions".to_string(),
            "0".to_string(), "LogConfiguration".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3046.validate(&validator, "Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions/*/LogConfiguration", instance, &serde_json::json!({}), &path);
        assert_eq!(errors.len(), 2); // missing awslogs-group and awslogs-region
    }
}

crate::register_cfn_lint_rule!(E3046);
