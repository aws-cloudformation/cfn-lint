use std::net::IpAddr;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3060: Validate subnet CIDRs do not overlap with other subnets in the same VPC.
pub struct E3060;

impl CfnLintRule for E3060 {
    fn id(&self) -> &str {
        "E3060"
    }
    fn short_description(&self) -> &str {
        "Validate subnet CIDRs do not overlap with other subnets"
    }
    fn description(&self) -> &str {
        "When specifying subnet CIDRs for a VPC the subnet CIDRs must not overlap with each other"
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
        let resources = match root.get("Resources").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        // Collect subnets grouped by VPC reference
        let mut vpc_subnets: std::collections::HashMap<String, Vec<SubnetInfo>> =
            std::collections::HashMap::new();

        for (name, node) in resources.iter() {
            let res = match template.resources.get(name) {
                Some(r) if r.resource_type == "AWS::EC2::Subnet" => r,
                _ => continue,
            };
            let props = match node.get("Properties") {
                Some(p) => p,
                None => continue,
            };

            let vpc_id = match get_vpc_ref(props) {
                Some(v) => v,
                None => continue,
            };

            for key in &["CidrBlock", "Ipv6CidrBlock"] {
                if let Some(cidr_str) = props.get(key).and_then(|n| n.as_str()) {
                    if let Some(net) = parse_cidr(cidr_str) {
                        vpc_subnets
                            .entry(vpc_id.clone())
                            .or_default()
                            .push(SubnetInfo {
                                resource_name: name.to_string(),
                                cidr: cidr_str.to_string(),
                                network: net,
                                span: props.get(key).map(|n| n.span().clone()).unwrap_or_default(),
                                condition: res.condition.clone(),
                            });
                    }
                }
            }
        }

        let mut issues = Vec::new();
        for (_vpc, subnets) in &vpc_subnets {
            for j in 1..subnets.len() {
                for i in 0..j {
                    // Skip if different conditions that are mutually exclusive
                    if let (Some(c1), Some(c2)) = (&subnets[i].condition, &subnets[j].condition) {
                        if c1 != c2 {
                            continue;
                        }
                    }
                    if networks_overlap(&subnets[i].network, &subnets[j].network) {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "'{}' overlaps with '{}'",
                                subnets[j].cidr, subnets[i].cidr
                            ),
                            path: vec![
                                "Resources".to_string(),
                                subnets[j].resource_name.clone(),
                                "Properties".to_string(),
                            ],
                            span: subnets[j].span.clone(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                        // Only report first overlap per subnet
                        break;
                    }
                }
            }
        }
        issues
    }
}

struct SubnetInfo {
    resource_name: String,
    cidr: String,
    network: Network,
    span: crate::ast::Span,
    condition: Option<String>,
}

#[derive(Clone)]
enum Network {
    V4 { addr: u32, prefix: u32 },
    V6 { addr: u128, prefix: u32 },
}

fn parse_cidr(s: &str) -> Option<Network> {
    let parts: Vec<&str> = s.split('/').collect();
    if parts.len() != 2 {
        return None;
    }
    let prefix: u32 = parts[1].parse().ok()?;
    let addr: IpAddr = parts[0].parse().ok()?;
    match addr {
        IpAddr::V4(v4) => {
            if prefix > 32 {
                return None;
            }
            let bits = u32::from(v4);
            let mask = if prefix == 0 {
                0
            } else {
                !0u32 << (32 - prefix)
            };
            Some(Network::V4 {
                addr: bits & mask,
                prefix,
            })
        }
        IpAddr::V6(v6) => {
            if prefix > 128 {
                return None;
            }
            let bits = u128::from(v6);
            let mask = if prefix == 0 {
                0
            } else {
                !0u128 << (128 - prefix)
            };
            Some(Network::V6 {
                addr: bits & mask,
                prefix,
            })
        }
    }
}

fn networks_overlap(a: &Network, b: &Network) -> bool {
    match (a, b) {
        (
            Network::V4 {
                addr: a_addr,
                prefix: a_pfx,
            },
            Network::V4 {
                addr: b_addr,
                prefix: b_pfx,
            },
        ) => {
            let min_pfx = std::cmp::min(*a_pfx, *b_pfx);
            let mask = if min_pfx == 0 {
                0
            } else {
                !0u32 << (32 - min_pfx)
            };
            (a_addr & mask) == (b_addr & mask)
        }
        (
            Network::V6 {
                addr: a_addr,
                prefix: a_pfx,
            },
            Network::V6 {
                addr: b_addr,
                prefix: b_pfx,
            },
        ) => {
            let min_pfx = std::cmp::min(*a_pfx, *b_pfx);
            let mask = if min_pfx == 0 {
                0
            } else {
                !0u128 << (128 - min_pfx)
            };
            (a_addr & mask) == (b_addr & mask)
        }
        _ => false,
    }
}

fn get_vpc_ref(props: &AstNode) -> Option<String> {
    let vpc_node = props.get("VpcId")?;
    if let Some(s) = vpc_node.as_str() {
        return Some(s.to_string());
    }
    if let Some(func) = vpc_node.as_function() {
        match func.name.as_str() {
            "Ref" => {
                if let Some(s) = func.args.as_str() {
                    return Some(s.to_string());
                }
            }
            "Fn::GetAtt" => {
                if let Some(s) = func.args.as_str() {
                    return Some(s.split('.').next()?.to_string());
                }
                if let Some(arr) = func.args.as_array() {
                    if let Some(first) = arr.elements.first().and_then(|e| e.as_str()) {
                        return Some(first.to_string());
                    }
                }
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
    fn test_no_overlap() {
        let yaml = br#"
Resources:
  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVpc
      CidrBlock: 10.0.1.0/24
  Subnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVpc
      CidrBlock: 10.0.2.0/24
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3060.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_overlapping_subnets() {
        let yaml = br#"
Resources:
  Subnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVpc
      CidrBlock: 10.0.0.0/24
  Subnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref MyVpc
      CidrBlock: 10.0.0.128/25
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3060.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("overlaps"));
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3060"));
    }
}

crate::register_cfn_lint_rule!(E3060);
