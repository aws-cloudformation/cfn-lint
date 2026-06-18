use std::net::Ipv4Addr;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

pub struct E3059;

impl CfnLintRule for E3059 {
    fn id(&self) -> &str { "E3059" }
    fn short_description(&self) -> &str {
        "Validate subnet CIDRs are within the CIDRs of the VPC"
    }
    fn description(&self) -> &str {
        "When specifying subnet CIDRs for a VPC the subnet CIDRs must be within the VPC CIDRs"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let resources_node = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        let mut issues = Vec::new();

        for (subnet_name, subnet_res) in &template.resources {
            if subnet_res.resource_type != "AWS::EC2::Subnet" {
                continue;
            }
            let subnet_props = match resources_node
                .get(subnet_name)
                .and_then(|n| n.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            // Get VpcId via Ref
            let vpc_name = match subnet_props.get("VpcId") {
                Some(AstNode::Function(f)) if f.name == "Ref" => {
                    match f.args.as_str() {
                        Some(s) => s,
                        None => continue,
                    }
                }
                _ => continue,
            };

            // Get subnet CIDR as string
            let subnet_cidr = match subnet_props.get("CidrBlock").and_then(|n| n.as_str()) {
                Some(s) => s,
                None => continue,
            };

            // Find VPC resource and its CidrBlock
            let vpc_props = match resources_node
                .get(vpc_name)
                .and_then(|n| n.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            let vpc_cidr = match vpc_props.get("CidrBlock").and_then(|n| n.as_str()) {
                Some(s) => s,
                None => continue,
            };

            if !cidr_contains(vpc_cidr, subnet_cidr) {
                issues.push(ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "Subnet CIDR '{}' is not within VPC CIDR '{}'",
                        subnet_cidr, vpc_cidr
                    ),
                    path: vec![
                        "Resources".to_string(),
                        subnet_name.clone(),
                        "Properties".to_string(),
                        "CidrBlock".to_string(),
                    ],
                    span: subnet_props
                        .get("CidrBlock")
                        .map(|n| n.span().clone())
                        .unwrap_or_default(),
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
});
            }
        }
        issues
    }
}

fn parse_cidr(cidr: &str) -> Option<(u32, u32)> {
    let parts: Vec<&str> = cidr.split('/').collect();
    if parts.len() != 2 {
        return None;
    }
    let ip: Ipv4Addr = parts[0].parse().ok()?;
    let prefix: u32 = parts[1].parse().ok()?;
    if prefix > 32 {
        return None;
    }
    let mask = if prefix == 0 { 0 } else { !0u32 << (32 - prefix) };
    let network = u32::from(ip) & mask;
    Some((network, mask))
}

fn cidr_contains(vpc_cidr: &str, subnet_cidr: &str) -> bool {
    let (vpc_net, vpc_mask) = match parse_cidr(vpc_cidr) {
        Some(v) => v,
        None => return true, // Can't parse, skip
    };
    let (subnet_net, subnet_mask) = match parse_cidr(subnet_cidr) {
        Some(v) => v,
        None => return true,
    };
    // Subnet prefix must be >= VPC prefix (smaller or equal network)
    // and subnet network must be within VPC network
    subnet_mask >= vpc_mask && (subnet_net & vpc_mask) == vpc_net
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_subnet_within_vpc() {
        let yaml = br#"
Resources:
  Vpc:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: "10.0.0.0/16"
  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref Vpc
      CidrBlock: "10.0.1.0/24"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3059.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_subnet_outside_vpc() {
        let yaml = br#"
Resources:
  Vpc:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: "10.0.0.0/16"
  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref Vpc
      CidrBlock: "192.168.1.0/24"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3059.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3059"));
        assert!(issues[0].message.contains("192.168.1.0/24"));
    }
}

crate::register_cfn_lint_rule!(E3059);
