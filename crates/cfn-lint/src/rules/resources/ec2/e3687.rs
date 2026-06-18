use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E3687;

const PROTOCOLS_REQUIRING_PORTS: &[&str] = &["1", "icmp", "6", "tcp", "17", "udp"];

impl E3687 {
    fn check_rule(
        &self,
        node: &AstNode,
        resource: &str,
        ctx: &str,
        issues: &mut Vec<ValidationError>,
    ) {
        let proto = match node.get("IpProtocol") {
            Some(p) => p,
            None => return,
        };
        let proto_val = match proto {
            AstNode::String(s) => s.value.clone(),
            AstNode::Number(n) => format!("{}", n.value as i64),
            AstNode::Function(_) => return,
            _ => return,
        };
        if !PROTOCOLS_REQUIRING_PORTS.contains(&proto_val.as_str()) {
            return;
        }
        let has_from = node.get("FromPort").is_some();
        let has_to = node.get("ToPort").is_some();
        if !has_from || !has_to {
            issues.push(ValidationError {
                rule_id: Some(self.id().to_string()),
                message: format!(
                    "['FromPort', 'ToPort'] are required properties when using 'IpProtocol' value {}",
                    proto_val
                ),
                path: vec!["Resources".into(), resource.into(), ctx.into()],
                span: node.span(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
});
        }
    }
}

impl CfnLintRule for E3687 {
    fn id(&self) -> &str {
        "E3687"
    }
    fn short_description(&self) -> &str {
        "Validate to and from ports based on the protocol"
    }
    fn description(&self) -> &str {
        "When using icmp, icmpv6, tcp, or udp you have to specify the to and from port ranges"
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
        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            match resource.resource_type.as_str() {
                "AWS::EC2::SecurityGroup" => {
                    let props = match root
                        .get("Resources")
                        .and_then(|r| r.get(name))
                        .and_then(|r| r.get("Properties"))
                    {
                        Some(p) => p,
                        None => continue,
                    };
                    for dir in &["SecurityGroupIngress", "SecurityGroupEgress"] {
                        if let Some(arr) = props.get(dir).and_then(|n| n.as_array()) {
                            for (i, rule) in arr.elements.iter().enumerate() {
                                self.check_rule(
                                    rule,
                                    name,
                                    &format!("Properties/{}/{}", dir, i),
                                    &mut issues,
                                );
                            }
                        }
                    }
                }
                "AWS::EC2::SecurityGroupIngress" | "AWS::EC2::SecurityGroupEgress" => {
                    if let Some(props) = root
                        .get("Resources")
                        .and_then(|r| r.get(name))
                        .and_then(|r| r.get("Properties"))
                    {
                        self.check_rule(props, name, "Properties", &mut issues);
                    }
                }
                _ => {}
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
    fn test_valid_with_ports() {
        let yaml = br#"
Resources:
  SG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: test
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3687.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_all_traffic_no_ports_ok() {
        let yaml = br#"
Resources:
  SG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: test
      SecurityGroupIngress:
        - IpProtocol: "-1"
          CidrIp: 0.0.0.0/0
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3687.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_missing_ports() {
        let yaml = br#"
Resources:
  SG:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: test
      SecurityGroupIngress:
        - IpProtocol: tcp
          CidrIp: 0.0.0.0/0
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3687.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
    }
}

crate::register_cfn_lint_rule!(E3687);
