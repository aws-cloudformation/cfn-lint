use std::collections::HashMap;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// A grouping key: (resource_condition, property_condition, subnet_value).
/// Conditioned resources only conflict with others sharing the same condition tuple,
/// and unconditional resources (None, None, val) conflict with everything sharing that subnet.
type SubnetKey = (Option<String>, Option<String>, String);

/// E3022: Validate there is only one SubnetRouteTableAssociation per subnet.
pub struct E3022;

impl CfnLintRule for E3022 {
    fn id(&self) -> &str {
        "E3022"
    }
    fn short_description(&self) -> &str {
        "Resource SubnetRouteTableAssociation Properties"
    }
    fn description(&self) -> &str {
        "Validate there is only one SubnetRouteTableAssociation per subnet"
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
        // Map SubnetKey -> list of resource names
        let mut key_to_resources: HashMap<SubnetKey, Vec<String>> = HashMap::new();
        // Map resource_name -> list of SubnetKeys
        let mut resource_values: HashMap<String, Vec<SubnetKey>> = HashMap::new();

        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::EC2::SubnetRouteTableAssociation" {
                continue;
            }
            let resource_condition = resource.condition.clone();
            let subnet_id = root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
                .and_then(|p| p.get("SubnetId"));

            if let Some(values) = subnet_id.map(|n| extract_values(n, &resource_condition, &None)) {
                resource_values.insert(name.clone(), values.clone());
                for val in values {
                    key_to_resources.entry(val).or_default().push(name.clone());
                }
            }
        }

        for (resource_name, values) in &resource_values {
            for value in values {
                let bare_value: SubnetKey = (None, None, value.2.clone());
                let mut other_resources: Vec<String> = Vec::new();

                // Same key duplicates
                if let Some(resources) = key_to_resources.get(value) {
                    for r in resources {
                        if r != resource_name {
                            other_resources.push(r.clone());
                        }
                    }
                }

                // Conditioned entries also conflict with bare (unconditioned) entries
                if *value != bare_value {
                    if let Some(resources) = key_to_resources.get(&bare_value) {
                        for r in resources {
                            if !other_resources.contains(r) {
                                other_resources.push(r.clone());
                            }
                        }
                    }
                }

                if !other_resources.is_empty() {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!(
                            "SubnetId in {} is also associated with {}",
                            resource_name,
                            other_resources.join(", ")
                        ),
                        path: vec![
                            "Resources".to_string(),
                            resource_name.to_string(),
                            "Properties".to_string(),
                            "SubnetId".to_string(),
                        ],
                        span: root
                            .get("Resources")
                            .and_then(|r| r.get(resource_name))
                            .and_then(|r| r.get("Properties"))
                            .and_then(|p| p.get("SubnetId"))
                            .map(|n| n.span())
                            .unwrap_or_default(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }
        }
        issues
    }
}

/// Extract (resource_condition, property_condition, value) tuples from a SubnetId node.
fn extract_values(
    node: &AstNode,
    resource_condition: &Option<String>,
    property_condition: &Option<String>,
) -> Vec<SubnetKey> {
    match node {
        AstNode::String(s) => vec![(
            resource_condition.clone(),
            property_condition.clone(),
            s.value.clone(),
        )],
        AstNode::Function(f) => match f.name.as_str() {
            "Ref" => {
                if let Some(s) = f.args.as_str() {
                    vec![(
                        resource_condition.clone(),
                        property_condition.clone(),
                        s.to_string(),
                    )]
                } else {
                    vec![]
                }
            }
            "Fn::If" => {
                if let Some(arr) = f.args.as_array() {
                    let mut vals = Vec::new();
                    if arr.elements.len() >= 3 {
                        let cond_name = arr.elements[0].as_str().map(|s| s.to_string());
                        vals.extend(extract_values(
                            &arr.elements[1],
                            resource_condition,
                            &cond_name,
                        ));
                        vals.extend(extract_values(
                            &arr.elements[2],
                            resource_condition,
                            &cond_name,
                        ));
                    }
                    vals
                } else {
                    vec![]
                }
            }
            "Fn::GetAtt" => {
                if let Some(arr) = f.args.as_array() {
                    if arr.elements.len() == 2 {
                        let parts: Vec<&str> =
                            arr.elements.iter().filter_map(|e| e.as_str()).collect();
                        if parts.len() == 2 {
                            return vec![(
                                resource_condition.clone(),
                                property_condition.clone(),
                                format!("{}.{}", parts[0], parts[1]),
                            )];
                        }
                    }
                } else if let Some(s) = f.args.as_str() {
                    return vec![(
                        resource_condition.clone(),
                        property_condition.clone(),
                        s.to_string(),
                    )];
                }
                vec![]
            }
            _ => vec![],
        },
        _ => vec![],
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_unique_subnet_associations() {
        let yaml = br#"
Resources:
  Assoc1:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: subnet-111
      RouteTableId: rtb-aaa
  Assoc2:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: subnet-222
      RouteTableId: rtb-bbb
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3022.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_duplicate_subnet_associations() {
        let yaml = br#"
Resources:
  Assoc1:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: subnet-111
      RouteTableId: rtb-aaa
  Assoc2:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      SubnetId: subnet-111
      RouteTableId: rtb-bbb
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3022.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 2);
        assert!(issues.iter().all(|i| i.rule_id.as_deref() == Some("E3022")));
    }
}

crate::register_cfn_lint_rule!(E3022);
