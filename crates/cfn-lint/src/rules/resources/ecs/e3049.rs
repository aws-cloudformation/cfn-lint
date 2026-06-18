use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E3049;

impl CfnLintRule for E3049 {
    fn id(&self) -> &str {
        "E3049"
    }
    fn short_description(&self) -> &str {
        "Validate ECS tasks with awsvpc network mode"
    }
    fn description(&self) -> &str {
        "When using awsvpc network mode, HostPort must equal ContainerPort (dynamic port mapping not supported)"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let resources_node = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        let mut issues = Vec::new();

        for (svc_name, svc_res) in &template.resources {
            if svc_res.resource_type != "AWS::ECS::Service" {
                continue;
            }
            let svc_props = match resources_node
                .get(svc_name)
                .and_then(|n| n.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            // Get the TaskDefinition reference
            let task_def_name = match svc_props.get("TaskDefinition") {
                Some(AstNode::Function(f)) if f.name == "Ref" => match f.args.as_str() {
                    Some(s) => s,
                    None => continue,
                },
                _ => continue,
            };

            // Find the referenced TaskDefinition resource
            match template.resources.get(task_def_name) {
                Some(r) if r.resource_type == "AWS::ECS::TaskDefinition" => {}
                _ => continue,
            }

            let task_props = match resources_node
                .get(task_def_name)
                .and_then(|n| n.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            // Check NetworkMode
            let network_mode = match task_props.get("NetworkMode").and_then(|n| n.as_str()) {
                Some(s) => s,
                None => continue,
            };
            if network_mode != "awsvpc" {
                continue;
            }

            // Check container definitions
            let containers = match task_props
                .get("ContainerDefinitions")
                .and_then(|n| n.as_array())
            {
                Some(a) => a,
                None => continue,
            };

            for (ci, container) in containers.elements.iter().enumerate() {
                let port_mappings = match container.get("PortMappings").and_then(|n| n.as_array()) {
                    Some(a) => a,
                    None => continue,
                };
                for (pi, mapping) in port_mappings.elements.iter().enumerate() {
                    let host_port = match mapping.get("HostPort").and_then(|n| n.as_f64()) {
                        Some(v) => v,
                        None => continue,
                    };
                    let container_port = match mapping.get("ContainerPort").and_then(|n| n.as_f64())
                    {
                        Some(v) => v,
                        None => continue,
                    };
                    if (host_port - container_port).abs() > f64::EPSILON {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "HostPort ({}) must equal ContainerPort ({}) when NetworkMode is awsvpc",
                                host_port as i64, container_port as i64
                            ),
                            path: vec![
                                "Resources".to_string(),
                                task_def_name.to_string(),
                                "Properties".to_string(),
                                "ContainerDefinitions".to_string(),
                                ci.to_string(),
                                "PortMappings".to_string(),
                                pi.to_string(),
                                "HostPort".to_string(),
                            ],
                            span: mapping.get("HostPort").map(|n| n.span().clone()).unwrap_or_default(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
});
                    }
                }
            }
        }
        issues
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_matching_ports_ok() {
        let yaml = br#"
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      NetworkMode: awsvpc
      ContainerDefinitions:
        - Name: app
          PortMappings:
            - ContainerPort: 8080
              HostPort: 8080
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDef
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3049.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_mismatched_ports_error() {
        let yaml = br#"
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      NetworkMode: awsvpc
      ContainerDefinitions:
        - Name: app
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDef
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3049.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3049"));
        assert!(issues[0].message.contains("HostPort"));
    }
}

crate::register_cfn_lint_rule!(E3049);
