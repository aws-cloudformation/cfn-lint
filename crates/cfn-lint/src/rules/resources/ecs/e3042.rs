use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3042: Validate at least one essential container is specified in ECS TaskDefinition.
pub struct E3042;

impl CfnLintRule for E3042 {
    fn id(&self) -> &str {
        "E3042"
    }
    fn short_description(&self) -> &str {
        "Validate at least one essential container is specified"
    }
    fn description(&self) -> &str {
        "Check that every TaskDefinition specifies at least one essential container"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let containers = match instance.as_array() {
            Some(c) => c,
            None => return vec![],
        };

        let has_essential = containers.elements.iter().any(|c| {
            match c.get("Essential") {
                Some(AstNode::Bool(b)) => b.value,
                Some(AstNode::Function(_)) => true, // can't resolve, assume ok
                None => true,                       // default is true
                _ => false,
            }
        });

        if !has_essential {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "At least one essential container is required".to_string(),
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
    fn test_has_essential_container() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: app
          Essential: true
          Image: nginx
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Task")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("ContainerDefinitions")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Task".to_string(),
            "Properties".to_string(),
            "ContainerDefinitions".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3042.validate(
            &validator,
            "Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_all_non_essential() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: sidecar
          Essential: false
          Image: fluentd
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Task")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("ContainerDefinitions")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Task".to_string(),
            "Properties".to_string(),
            "ContainerDefinitions".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3042.validate(
            &validator,
            "Resources/AWS::ECS::TaskDefinition/Properties/ContainerDefinitions",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("essential"));
    }
}

crate::register_cfn_lint_rule!(E3042);
