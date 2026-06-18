use std::collections::HashMap;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E3064: Validate unique PrivateDnsEnabled per service per VPC
pub struct E3064;

impl CfnLintRule for E3064 {
    fn id(&self) -> &str { "E3064" }
    fn short_description(&self) -> &str {
        "Validate unique PrivateDnsEnabled per service per VPC"
    }
    fn description(&self) -> &str {
        "Only one Interface VPC Endpoint per service can have PrivateDnsEnabled \
         set to true in a VPC. A second endpoint will fail to create due to a \
         conflicting private DNS domain."
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let mut issues = Vec::new();
        // Group: (vpc_key, service_key) -> first resource name
        let mut seen: HashMap<(String, String), String> = HashMap::new();

        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::EC2::VPCEndpoint" {
                continue;
            }
            let props = match root
                .get("Resources").and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            // Must be Interface type
            let endpoint_type = props.get("VpcEndpointType").and_then(|n| n.as_str());
            if endpoint_type != Some("Interface") {
                continue;
            }

            // PrivateDnsEnabled must be true
            let private_dns = props.get("PrivateDnsEnabled").and_then(|n| n.as_bool());
            if private_dns != Some(true) {
                continue;
            }

            let vpc_key = resolve_key(props.get("VpcId"));
            let svc_key = resolve_key(props.get("ServiceName"));

            if let (Some(vk), Some(sk)) = (vpc_key, svc_key) {
                let group = (vk, sk);
                if let Some(first) = seen.get(&group) {
                    issues.push(ValidationError {
                        rule_id: Some("E3064".to_string()),
                        message: format!(
                            "Only one Interface VPC Endpoint per service can have \
                             'PrivateDnsEnabled' set to true in a VPC. Conflicts with '{}'.",
                            first
                        ),
                        path: vec!["Resources".to_string(), name.clone(), "Properties".to_string()],
                        span: props.span(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
});
                } else {
                    seen.insert(group, name.clone());
                }
            }
        }
        issues
    }
}

fn resolve_key(node: Option<&AstNode>) -> Option<String> {
    let node = node?;
    if let Some(s) = node.as_str() {
        return Some(s.to_string());
    }
    if let Some(func) = node.as_function() {
        match func.name.as_str() {
            "Ref" => {
                if let Some(s) = func.args.as_str() {
                    return Some(format!("Ref:{}", s));
                }
            }
            "Fn::GetAtt" => {
                return Some(format!("GetAtt:{}", func.args));
            }
            _ => {}
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_duplicate_private_dns() {
        let yaml = br#"
Resources:
  Endpoint1:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: vpc-123
      ServiceName: com.amazonaws.us-east-1.s3
      VpcEndpointType: Interface
      PrivateDnsEnabled: true
  Endpoint2:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: vpc-123
      ServiceName: com.amazonaws.us-east-1.s3
      VpcEndpointType: Interface
      PrivateDnsEnabled: true
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3064.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_no_duplicate_different_service() {
        let yaml = br#"
Resources:
  Endpoint1:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: vpc-123
      ServiceName: com.amazonaws.us-east-1.s3
      VpcEndpointType: Interface
      PrivateDnsEnabled: true
  Endpoint2:
    Type: AWS::EC2::VPCEndpoint
    Properties:
      VpcId: vpc-123
      ServiceName: com.amazonaws.us-east-1.ec2
      VpcEndpointType: Interface
      PrivateDnsEnabled: true
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3064.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3064);
