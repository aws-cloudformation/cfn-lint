use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3048: Validate ECS Fargate tasks have required properties and values.
pub struct E3048;

impl CfnLintRule for E3048 {
    fn id(&self) -> &str {
        "E3048"
    }
    fn short_description(&self) -> &str {
        "Validate ECS Fargate tasks have required properties and values"
    }
    fn description(&self) -> &str {
        "When using an ECS Fargate task there is a specific combination \
         of required properties and values"
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

        // Check if this is a Fargate task. RequiresCompatibilities may be a
        // plain array or wrapped in Fn::If, so descend into conditional
        // branches rather than giving up when as_array() returns None (C70).
        let is_fargate = props
            .get("RequiresCompatibilities")
            .map(mentions_fargate)
            .unwrap_or(false);
        if !is_fargate {
            return vec![];
        }

        let mut errors = Vec::new();

        // NetworkMode is required for Fargate
        match props.get("NetworkMode") {
            Some(mode_node) => {
                if let Some(mode) = mode_node.as_str() {
                    if mode != "awsvpc" {
                        let mut mode_path = path.to_vec();
                        mode_path.push("NetworkMode".to_string());
                        errors.push(ValidationError {
                            rule_id: None,
                            keyword: format!("cfnLint:{}", self.id()),
                            message: format!(
                                "Fargate tasks must use 'awsvpc' NetworkMode, got '{}'",
                                mode
                            ),
                            path: mode_path,
                            span: mode_node.span(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                }
            }
            None => {
                errors.push(ValidationError {
                    rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: "'NetworkMode' is a required property".to_string(),
                    path: path.to_vec(),
                    span: instance.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
            }
        }

        // Cpu is required for Fargate
        match props.get("Cpu") {
            Some(cpu_node) => {
                if let Some(cpu) = cpu_node.as_str() {
                    if !VALID_FARGATE_CPU.contains(&cpu) {
                        let mut cpu_path = path.to_vec();
                        cpu_path.push("Cpu".to_string());
                        errors.push(ValidationError {
                            rule_id: None,
                            keyword: format!("cfnLint:{}", self.id()),
                            message: format!(
                                "Fargate task has invalid Cpu value '{}'. Must be one of {:?}",
                                cpu, VALID_FARGATE_CPU
                            ),
                            path: cpu_path,
                            span: cpu_node.span(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                }
            }
            None => {
                errors.push(ValidationError {
                    rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: "'Cpu' is a required property".to_string(),
                    path: path.to_vec(),
                    span: instance.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
            }
        }

        // Memory is required for Fargate
        if props.get("Memory").is_none() {
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "'Memory' is a required property".to_string(),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }

        // PlacementConstraints not supported for Fargate
        if let Some(pc_node) = props.get("PlacementConstraints") {
            let mut pc_path = path.to_vec();
            pc_path.push("PlacementConstraints".to_string());
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "'PlacementConstraints' isn't supported for Fargate tasks".to_string(),
                path: pc_path,
                span: pc_node.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }

        errors
    }
}

const VALID_FARGATE_CPU: &[&str] = &["256", "512", "1024", "2048", "4096", "8192", "16384"];

/// Determine whether `RequiresCompatibilities` requests FARGATE, descending
/// into `Fn::If` branches so a conditional value does not silently disable
/// the rule (C70). Both the True (index 1) and False (index 2) branches of
/// each `Fn::If` are inspected.
fn mentions_fargate(node: &AstNode) -> bool {
    match node {
        AstNode::String(s) => s.value == "FARGATE",
        AstNode::Array(arr) => arr.elements.iter().any(mentions_fargate),
        AstNode::Function(func) if func.name == "Fn::If" => match func.args.as_array() {
            // Skip the condition name (index 0); check both branches.
            Some(arr) => arr.elements.iter().skip(1).any(mentions_fargate),
            None => false,
        },
        _ => false,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_fargate_task() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      RequiresCompatibilities:
        - FARGATE
      NetworkMode: awsvpc
      Cpu: "256"
      Memory: "512"
      ContainerDefinitions:
        - Name: app
          Image: nginx
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
        let errors = E3048.validate(
            &validator,
            "Resources/AWS::ECS::TaskDefinition/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_fargate_with_placement_constraints() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      RequiresCompatibilities:
        - FARGATE
      NetworkMode: awsvpc
      Cpu: "256"
      Memory: "512"
      PlacementConstraints:
        - Type: memberOf
      ContainerDefinitions:
        - Name: app
          Image: nginx
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
        let errors = E3048.validate(
            &validator,
            "Resources/AWS::ECS::TaskDefinition/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("PlacementConstraints"));
    }

    // C69: 8 vCPU (8192) and 16 vCPU (16384) are valid Fargate CPU values.
    #[test]
    fn test_valid_fargate_high_cpu_values() {
        for cpu in ["8192", "16384"] {
            let yaml = format!(
                r#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      RequiresCompatibilities:
        - FARGATE
      NetworkMode: awsvpc
      Cpu: "{}"
      Memory: "32768"
      ContainerDefinitions:
        - Name: app
          Image: nginx
"#,
                cpu
            );
            let ast = parser::parse(yaml.as_bytes()).unwrap();
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
            let errors = E3048.validate(
                &validator,
                "Resources/AWS::ECS::TaskDefinition/Properties",
                instance,
                &serde_json::json!({}),
                &path,
            );
            assert!(
                errors.is_empty(),
                "cpu {} should be valid, got: {:?}",
                cpu,
                errors
            );
        }
    }

    // C70: Fn::If in RequiresCompatibilities must not silently disable the
    // rule. With FARGATE in a branch, the required-property checks still run.
    #[test]
    fn test_fargate_via_fn_if_still_validated() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      RequiresCompatibilities:
        Fn::If:
          - UseFargate
          - - FARGATE
          - - EC2
      ContainerDefinitions:
        - Name: app
          Image: nginx
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
        let errors = E3048.validate(
            &validator,
            "Resources/AWS::ECS::TaskDefinition/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        // NetworkMode, Cpu, and Memory are all missing -> three errors.
        assert_eq!(errors.len(), 3, "got: {:?}", errors);
    }
}

crate::register_cfn_lint_rule!(E3048);
