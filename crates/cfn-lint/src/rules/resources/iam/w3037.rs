use std::collections::HashMap;
use std::sync::LazyLock;

use crate::ast::{AstNode, Span};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

static POLICIES: LazyLock<Option<HashMap<String, HashMap<String, ()>>>> = LazyLock::new(|| {
    let raw: serde_json::Value = serde_json::from_str(include_str!(
        "../../../../data/additional_specs/Policies.json"
    ))
    .ok()?;
    let obj = raw.as_object()?;
    let mut map = HashMap::new();
    for (service, svc_val) in obj {
        let actions = svc_val.get("Actions")?.as_object()?;
        let action_map: HashMap<String, ()> =
            actions.keys().map(|k| (k.to_lowercase(), ())).collect();
        map.insert(service.to_lowercase(), action_map);
    }
    Some(map)
});

/// W3037: Check IAM Permission configuration.
/// Validates that IAM actions use valid service:action format and match known services/actions.
pub struct W3037;

impl CfnLintRule for W3037 {
    fn id(&self) -> &str {
        "W3037"
    }
    fn short_description(&self) -> &str {
        "Check IAM Permission configuration"
    }
    fn description(&self) -> &str {
        "Check for valid IAM Permissions"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let service_map = match POLICIES.as_ref() {
            Some(m) => m,
            None => return vec![],
        };

        // Check if template has serverless transform - skip if so
        if has_serverless_transform(root) {
            return vec![];
        }

        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            let props = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            let limitations = resource_action_limitations(&resource.resource_type);

            // Find Statement/Action paths depending on resource type
            let statements = find_statements(props, &resource.resource_type);
            for (stmt, stmt_path) in statements {
                let actions_node = match stmt.get("Action") {
                    Some(a) => a,
                    None => continue,
                };

                let action_list = collect_actions(actions_node);
                for (action_str, action_pos) in &action_list {
                    let mut action_path = stmt_path.clone();
                    action_path.push("Action".to_string());

                    if action_str == "*" {
                        continue;
                    }
                    if !action_str.contains(':') {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!(
                                "'{}' is not a valid action. Must be of the form service:action or '*'",
                                action_str
                            ),
                            path: prepend_resource_path(name, &action_path),
                            span: action_pos.clone(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
});
                        continue;
                    }

                    let parts: Vec<&str> = action_str.splitn(2, ':').collect();
                    let service = parts[0].to_lowercase();
                    let permission = parts[1].to_lowercase();

                    // Check resource-specific limitations
                    if let Some(allowed) = limitations {
                        if !allowed.contains(&service.as_str()) {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!("'{}' is not one of {:?}", service, allowed),
                                path: prepend_resource_path(name, &action_path),
                                span: action_pos.clone(),
                                keyword: String::new(),
                                unknown: false,
                                resolved_from_ref: false,
                                context: vec![],
                                schema_id: None,
                            });
                        }
                    }

                    if let Some(svc_data) = service_map.get(&service) {
                        let enums: Vec<&String> = svc_data.keys().collect();
                        if permission == "*" {
                            continue;
                        }
                        if permission.contains('*') || permission.contains('?') {
                            let pattern =
                                format!("^{}$", permission.replace('*', ".*").replace('?', "."));
                            if let Ok(re) = regex::Regex::new(&pattern) {
                                if !enums.iter().any(|e| re.is_match(e)) {
                                    issues.push(ValidationError {
                                        rule_id: Some(self.id().to_string()),
                                        message: format!(
                                            "'{}' does not match any known actions",
                                            permission
                                        ),
                                        path: prepend_resource_path(name, &action_path),
                                        span: action_pos.clone(),
                                        keyword: String::new(),
                                        unknown: false,
                                        resolved_from_ref: false,
                                        context: vec![],
                                        schema_id: None,
                                    });
                                }
                            }
                        } else if !svc_data.contains_key(&permission) {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!(
                                    "'{}' is not a valid action for service '{}'",
                                    permission, service
                                ),
                                path: prepend_resource_path(name, &action_path),
                                span: action_pos.clone(),
                                keyword: String::new(),
                                unknown: false,
                                resolved_from_ref: false,
                                context: vec![],
                                schema_id: None,
                            });
                        }
                    } else {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!("'{}' is not a valid IAM service", service),
                            path: prepend_resource_path(name, &action_path),
                            span: action_pos.clone(),
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

// Resource types that restrict which service actions are allowed
fn resource_action_limitations(resource_type: &str) -> Option<&[&str]> {
    match resource_type {
        "AWS::S3::BucketPolicy" => Some(&["s3"]),
        "AWS::SQS::QueuePolicy" => Some(&["sqs"]),
        "AWS::SNS::TopicPolicy" => Some(&["sns"]),
        _ => None,
    }
}

fn prepend_resource_path(name: &str, path: &[String]) -> Vec<String> {
    let mut full = vec![
        "Resources".to_string(),
        name.to_string(),
        "Properties".to_string(),
    ];
    full.extend(path.iter().cloned());
    full
}

fn has_serverless_transform(root: &AstNode) -> bool {
    match root.get("Transform") {
        Some(AstNode::String(s)) => s.value.contains("Serverless"),
        Some(AstNode::Array(arr)) => arr.elements.iter().any(|e| {
            e.as_str()
                .map(|s| s.contains("Serverless"))
                .unwrap_or(false)
        }),
        _ => false,
    }
}

/// Find all Statement arrays in the resource properties
fn find_statements<'a>(props: &'a AstNode, resource_type: &str) -> Vec<(&'a AstNode, Vec<String>)> {
    let mut results = Vec::new();
    let policy_paths: Vec<Vec<&str>> = match resource_type {
        "AWS::IAM::Policy" => vec![vec!["PolicyDocument", "Statement"]],
        "AWS::IAM::Role" => vec![
            vec!["AssumeRolePolicyDocument", "Statement"],
            vec!["Policies", "*", "PolicyDocument", "Statement"],
        ],
        "AWS::IAM::ManagedPolicy" => vec![vec!["PolicyDocument", "Statement"]],
        "AWS::S3::BucketPolicy" | "AWS::SQS::QueuePolicy" | "AWS::SNS::TopicPolicy" => {
            vec![vec!["PolicyDocument", "Statement"]]
        }
        _ => return results,
    };

    for path_parts in &policy_paths {
        collect_statements_at_path(props, path_parts, &[], &mut results);
    }
    results
}

fn collect_statements_at_path<'a>(
    node: &'a AstNode,
    remaining: &[&str],
    current_path: &[String],
    results: &mut Vec<(&'a AstNode, Vec<String>)>,
) {
    if remaining.is_empty() {
        // We should be at a Statement array
        if let Some(arr) = node.as_array() {
            for (i, stmt) in arr.elements.iter().enumerate() {
                let mut p = current_path.to_vec();
                p.push(i.to_string());
                results.push((stmt, p));
            }
        }
        return;
    }

    let key = remaining[0];
    let rest = &remaining[1..];

    if key == "*" {
        if let Some(arr) = node.as_array() {
            for (i, elem) in arr.elements.iter().enumerate() {
                let mut p = current_path.to_vec();
                p.push(i.to_string());
                collect_statements_at_path(elem, rest, &p, results);
            }
        }
    } else if let Some(child) = node.get(key) {
        let mut p = current_path.to_vec();
        p.push(key.to_string());
        collect_statements_at_path(child, rest, &p, results);
    }
}

fn collect_actions(node: &AstNode) -> Vec<(String, Span)> {
    match node {
        AstNode::String(s) => vec![(s.value.clone(), s.span.clone())],
        AstNode::Array(arr) => arr
            .elements
            .iter()
            .filter_map(|e| {
                if let AstNode::String(s) = e {
                    Some((s.value.clone(), s.span.clone()))
                } else {
                    None
                }
            })
            .collect(),
        _ => vec![],
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_iam_actions() {
        let yaml = br#"
Resources:
  MyPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: test
      PolicyDocument:
        Statement:
          - Effect: Allow
            Action:
              - s3:GetObject
              - s3:PutObject
            Resource: "*"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W3037.validate_template(&tmpl, &ast);
        assert!(
            issues.is_empty(),
            "Expected no issues but got: {:?}",
            issues
        );
    }

    #[test]
    fn test_invalid_action_format() {
        let yaml = br#"
Resources:
  MyPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: test
      PolicyDocument:
        Statement:
          - Effect: Allow
            Action: InvalidAction
            Resource: "*"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W3037.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("not a valid action"));
    }
}

crate::register_cfn_lint_rule!(W3037);
