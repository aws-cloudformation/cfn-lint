use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3053: Validate ECS task definition HostPort equals ContainerPort when NetworkMode is awsvpc.
///
/// When NetworkMode is 'awsvpc', the HostPort must either be undefined or
/// equal to the ContainerPort value.
pub struct E3053;

impl CfnLintRule for E3053 {
    fn id(&self) -> &str {
        "E3053"
    }
    fn short_description(&self) -> &str {
        "Validate ECS task definition has correct values for HostPort"
    }
    fn description(&self) -> &str {
        "The HostPort must either be undefined or equal to the ContainerPort value when NetworkMode is awsvpc"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::ECS::TaskDefinition/Properties"]
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

        let network_mode = match props.get("NetworkMode").and_then(|n| n.as_str()) {
            Some(m) => m,
            None => return vec![],
        };
        if network_mode != "awsvpc" {
            return vec![];
        }

        let containers = match props.get("ContainerDefinitions").and_then(|n| n.as_array()) {
            Some(a) => a,
            None => return vec![],
        };

        let mut errors = Vec::new();
        for container in &containers.elements {
            let mappings = match container.get("PortMappings").and_then(|n| n.as_array()) {
                Some(a) => a,
                None => continue,
            };
            for mapping in &mappings.elements {
                let host_port = match mapping.get("HostPort") {
                    Some(hp) => hp,
                    None => continue,
                };
                let container_port = match mapping.get("ContainerPort") {
                    Some(cp) => cp,
                    None => continue,
                };
                let hp_val = host_port
                    .as_f64()
                    .or_else(|| host_port.as_str().and_then(|s| s.parse::<f64>().ok()));
                let cp_val = container_port
                    .as_f64()
                    .or_else(|| container_port.as_str().and_then(|s| s.parse::<f64>().ok()));
                if let (Some(hp), Some(cp)) = (hp_val, cp_val) {
                    if (hp - cp).abs() > f64::EPSILON {
                        let mut err_path = path.to_vec();
                        err_path.push("ContainerDefinitions".to_string());
                        errors.push(ValidationError {
                rule_id: None,
                            keyword: format!("cfnLint:{}", self.id()),
                            message: format!(
                                "HostPort {} does not equal ContainerPort {} when NetworkMode is 'awsvpc'",
                                hp as i64, cp as i64
                            ),
                            path: err_path,
                            span: host_port.span(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                }
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
    fn test_matching_ports_no_issue() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      NetworkMode: awsvpc
      ContainerDefinitions:
        - Name: app
          PortMappings:
            - ContainerPort: 80
              HostPort: 80
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Task")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Task".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3053.validate(
            &validator,
            "Resources/AWS::ECS::TaskDefinition/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_mismatched_ports() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      NetworkMode: awsvpc
      ContainerDefinitions:
        - Name: app
          PortMappings:
            - ContainerPort: 80
              HostPort: 8080
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Task")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Task".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3053.validate(
            &validator,
            "Resources/AWS::ECS::TaskDefinition/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("8080"));
    }
}

crate::register_cfn_lint_rule!(E3053);
