use crate::ast::{AstNode, FunctionNode, Span};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// Error message, kept identical to Python cfn-lint's `ServiceDynamicPorts`.
const MESSAGE: &str = "When using an ECS task definition of host port 0 and associating that \
container to an ELB the target group has to have a 'HealthCheckPort' of 'traffic-port'";

/// E3049: Validate ECS tasks with a dynamic host port have traffic-port ELB target groups.
///
/// Mirrors Python cfn-lint's `ServiceDynamicPorts`: when an ECS task definition uses a
/// dynamic host port (`HostPort: 0`) and the associated container is wired to an ELB via
/// the Service's `LoadBalancers`, the referenced target group must set
/// `HealthCheckPort: traffic-port`.
///
/// (The awsvpc `HostPort == ContainerPort` constraint is E3053's responsibility.)
pub struct E3049;

impl CfnLintRule for E3049 {
    fn id(&self) -> &str {
        "E3049"
    }
    fn short_description(&self) -> &str {
        "Validate ECS tasks with dynamic host port have traffic-port ELB target groups"
    }
    fn description(&self) -> &str {
        MESSAGE
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<ValidationError> {
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

            // Resolve the Service's TaskDefinition to a resource name (Ref or Fn::GetAtt).
            let task_def_name = match svc_props
                .get("TaskDefinition")
                .and_then(filter_resource_name)
            {
                Some(n) => n,
                None => continue,
            };
            // It must point at an actual ECS TaskDefinition resource.
            match template.resources.get(&task_def_name) {
                Some(r) if r.resource_type == "AWS::ECS::TaskDefinition" => {}
                _ => continue,
            }
            let task_props = match resources_node
                .get(&task_def_name)
                .and_then(|n| n.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            let load_balancers = match svc_props.get("LoadBalancers").and_then(|n| n.as_array()) {
                Some(a) => a,
                None => continue,
            };

            for lb in &load_balancers.elements {
                // ContainerName must be a concrete string to correlate with the task.
                let container_name = match lb.get("ContainerName").and_then(|n| n.as_str()) {
                    Some(s) => s,
                    None => continue,
                };
                // ContainerPort must be a concrete scalar (string/int) to correlate.
                let lb_container_port = match lb.get("ContainerPort").and_then(scalar_to_string) {
                    Some(s) => s,
                    None => continue,
                };
                // TargetGroupArn must resolve to a resource name (Ref or Fn::GetAtt).
                let tg_name = match lb.get("TargetGroupArn").and_then(filter_resource_name) {
                    Some(n) => n,
                    None => continue,
                };

                // Only a dynamic (HostPort: 0) mapping for the associated container/port matters.
                if !task_has_dynamic_port(task_props, container_name, &lb_container_port) {
                    continue;
                }

                // The referenced resource must be an ELBv2 target group to assert on it.
                match template.resources.get(&tg_name) {
                    Some(r) if r.resource_type == "AWS::ElasticLoadBalancingV2::TargetGroup" => {}
                    _ => continue,
                }

                let tg_props = resources_node
                    .get(&tg_name)
                    .and_then(|n| n.get("Properties"));

                match tg_props.and_then(|p| p.get("HealthCheckPort")) {
                    // Missing HealthCheckPort → must be present and 'traffic-port'.
                    None => {
                        let span = tg_props
                            .or_else(|| resources_node.get(&tg_name))
                            .map(|n| n.span())
                            .unwrap_or_default();
                        issues.push(health_check_error(&tg_name, span));
                    }
                    Some(hc) => match scalar_to_string(hc) {
                        // Correct value; nothing to report.
                        Some(ref s) if s == "traffic-port" => {}
                        // Present but not 'traffic-port'.
                        Some(_) => issues.push(health_check_error(&tg_name, hc.span())),
                        // Non-scalar (Ref/intrinsic): can't assert statically, skip (parity).
                        None => {}
                    },
                }
            }
        }
        issues
    }
}

/// Build the E3049 validation error pointing at a target group's `HealthCheckPort`.
fn health_check_error(tg_name: &str, span: Span) -> ValidationError {
    ValidationError::new(
        "E3049",
        MESSAGE,
        vec![
            "Resources".to_string(),
            tg_name.to_string(),
            "Properties".to_string(),
            "HealthCheckPort".to_string(),
        ],
        span,
    )
}

/// Resolve a `Ref` / `Fn::GetAtt` node to the referenced logical resource name.
/// Returns `None` for any other node (e.g. plain strings, `Fn::FindInMap`, `Ref: []`).
fn filter_resource_name(node: &AstNode) -> Option<String> {
    let func = node.as_function()?;
    match func.name.as_str() {
        "Ref" => func.args.as_str().map(|s| s.to_string()),
        "Fn::GetAtt" => parse_getatt_resource(func),
        _ => None,
    }
}

/// Extract just the logical-resource-name portion of an `Fn::GetAtt`.
fn parse_getatt_resource(func: &FunctionNode) -> Option<String> {
    crate::rules::e3015::parse_getatt_args(func).map(|(resource, _attr)| resource)
}

/// Stringify a scalar node the way Python's `str(...)` would for `str`/`int` values.
/// Strings pass through; integer-valued numbers render without a decimal point.
/// Everything else (floats, bools, functions, arrays, objects, null) yields `None`,
/// matching Python's `isinstance(value, (str, int))` guard.
fn scalar_to_string(node: &AstNode) -> Option<String> {
    match node {
        AstNode::String(s) => Some(s.value.clone()),
        AstNode::Number(n) if n.value.fract() == 0.0 => Some(format!("{}", n.value as i64)),
        _ => None,
    }
}

/// Does `task_props` define a container named `container_name` whose `PortMappings`
/// contains a mapping for `container_port` (string-compared) with a dynamic `HostPort` (0)?
fn task_has_dynamic_port(task_props: &AstNode, container_name: &str, container_port: &str) -> bool {
    let containers = match task_props
        .get("ContainerDefinitions")
        .and_then(|n| n.as_array())
    {
        Some(a) => a,
        None => return false,
    };

    for container in &containers.elements {
        match container.get("Name").and_then(|n| n.as_str()) {
            Some(name) if name == container_name => {}
            _ => continue,
        }
        let mappings = match container.get("PortMappings").and_then(|n| n.as_array()) {
            Some(a) => a,
            None => continue,
        };
        for mapping in &mappings.elements {
            match mapping.get("ContainerPort").and_then(scalar_to_string) {
                Some(ref cp) if cp == container_port => {}
                _ => continue,
            }
            if let Some(hp) = mapping.get("HostPort").and_then(scalar_to_string) {
                if hp == "0" {
                    return true;
                }
            }
        }
    }
    false
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    fn run(yaml: &[u8]) -> Vec<ValidationError> {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        E3049.validate_template(&tmpl, &ast)
    }

    #[test]
    fn test_dynamic_port_wrong_health_check_port_errors() {
        let yaml = br#"
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: my-container
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: "3000"
      Port: 8080
      Protocol: HTTP
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref TargetGroup
          ContainerName: my-container
          ContainerPort: 8080
"#;
        let issues = run(yaml);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3049"));
        assert_eq!(
            issues[0].path,
            vec!["Resources", "TargetGroup", "Properties", "HealthCheckPort"]
        );
    }

    #[test]
    fn test_dynamic_port_traffic_port_ok() {
        let yaml = br#"
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: my-container
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: traffic-port
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref TargetGroup
          ContainerName: my-container
          ContainerPort: 8080
"#;
        assert!(run(yaml).is_empty());
    }

    #[test]
    fn test_non_dynamic_port_ok() {
        let yaml = br#"
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: my-container
          PortMappings:
            - ContainerPort: 8080
              HostPort: 8080
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: "3000"
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref TargetGroup
          ContainerName: my-container
          ContainerPort: 8080
"#;
        assert!(run(yaml).is_empty());
    }

    #[test]
    fn test_missing_health_check_port_errors() {
        let yaml = br#"
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: my-container
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Port: 8080
      Protocol: HTTP
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref TargetGroup
          ContainerName: my-container
          ContainerPort: 8080
"#;
        let issues = run(yaml);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3049"));
    }

    #[test]
    fn test_task_definition_getatt_reference_errors() {
        // Parity with Python: a Fn::GetAtt task-definition reference is resolved too.
        let yaml = br#"
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: my-container
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: "3000"
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !GetAtt TaskDef.Arn
      LoadBalancers:
        - TargetGroupArn: !Ref TargetGroup
          ContainerName: my-container
          ContainerPort: 8080
"#;
        let issues = run(yaml);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3049"));
    }

    #[test]
    fn test_container_name_mismatch_ok() {
        let yaml = br#"
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: my-container
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: "3000"
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref TargetGroup
          ContainerName: other-container
          ContainerPort: 8080
"#;
        assert!(run(yaml).is_empty());
    }

    #[test]
    fn test_multiple_services_only_bad_one_reports() {
        // Good (traffic-port), Bad (wrong port), and Static (non-dynamic) services
        // coexist; only the Bad one must report, and against its own target group.
        let yaml = br#"
Resources:
  GoodTaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: app
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  GoodTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: traffic-port
  GoodService:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref GoodTaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref GoodTargetGroup
          ContainerName: app
          ContainerPort: 8080
  BadTaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: app
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  BadTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: "3000"
  BadService:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref BadTaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref BadTargetGroup
          ContainerName: app
          ContainerPort: 8080
  StaticTaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: app
          PortMappings:
            - ContainerPort: 8080
              HostPort: 8080
  StaticTargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: "3000"
  StaticService:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref StaticTaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref StaticTargetGroup
          ContainerName: app
          ContainerPort: 8080
"#;
        let issues = run(yaml);
        assert_eq!(issues.len(), 1);
        assert_eq!(
            issues[0].path,
            vec![
                "Resources",
                "BadTargetGroup",
                "Properties",
                "HealthCheckPort"
            ]
        );
    }

    #[test]
    fn test_health_check_port_non_scalar_ok() {
        // A Ref/intrinsic HealthCheckPort can't be asserted statically; no error (parity).
        let yaml = br#"
Parameters:
  MyHealthCheckPort:
    Type: String
Resources:
  TaskDef:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ContainerDefinitions:
        - Name: my-container
          PortMappings:
            - ContainerPort: 8080
              HostPort: 0
  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      HealthCheckPort: !Ref MyHealthCheckPort
  Service:
    Type: AWS::ECS::Service
    Properties:
      TaskDefinition: !Ref TaskDef
      LoadBalancers:
        - TargetGroupArn: !Ref TargetGroup
          ContainerName: my-container
          ContainerPort: 8080
"#;
        assert!(run(yaml).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3049);
