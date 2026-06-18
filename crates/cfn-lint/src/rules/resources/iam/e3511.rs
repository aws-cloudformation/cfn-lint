use regex::Regex;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3511: Validate IAM role ARN pattern.
///
/// Checks that IAM role ARN values match the expected pattern
/// `arn:(aws[a-zA-Z-]*)?:iam::\d{12}:role/[a-zA-Z_0-9+=,.@\-_/]+`.
/// Applies to specific resource properties that expect a role ARN.
pub struct E3511;

impl CfnLintRule for E3511 {
    fn id(&self) -> &str {
        "E3511"
    }
    fn short_description(&self) -> &str {
        "Validate IAM role arn pattern"
    }
    fn description(&self) -> &str {
        "Validate an IAM role ARN pattern matches the expected format"
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
        let re = match Regex::new(ROLE_ARN_PATTERN) {
            Ok(r) => r,
            Err(_) => return vec![],
        };
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
            for &(res_type, prop_path) in ROLE_ARN_PATHS {
                if resource.resource_type != res_type {
                    continue;
                }
                let node = match resolve_path(props, prop_path) {
                    Some(n) => n,
                    None => continue,
                };
                if let Some(arn) = node.as_str() {
                    if !re.is_match(arn) {
                        let mut path = vec!["Resources".into(), name.clone(), "Properties".into()];
                        path.extend(prop_path.split('/').map(String::from));
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!("'{}' does not match '{}'", arn, ROLE_ARN_PATTERN),
                            path,
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
        }
        issues
    }
}

const ROLE_ARN_PATHS: &[(&str, &str)] = &[
    ("AWS::Backup::BackupSelection", "BackupSelection/IamRoleArn"),
    (
        "AWS::Batch::ComputeEnvironment",
        "ComputeResources/SpotIamFleetRole",
    ),
    ("AWS::Batch::ComputeEnvironment", "ServiceRole"),
    (
        "AWS::EC2::SpotFleet",
        "SpotFleetRequestConfigData/IamFleetRole",
    ),
    ("AWS::ECS::TaskDefinition", "ExecutionRoleArn"),
    ("AWS::S3::Bucket", "ReplicationConfiguration/Role"),
];

const ROLE_ARN_PATTERN: &str = r"^arn:(aws[a-zA-Z-]*)?:iam::\d{12}:role/[a-zA-Z_0-9+=,.@\-_/]+$";

fn resolve_path<'a>(node: &'a AstNode, path: &str) -> Option<&'a AstNode> {
    let mut current = node;
    for segment in path.split('/') {
        current = current.get(segment)?;
    }
    Some(current)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_role_arn() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ExecutionRoleArn: arn:aws:iam::123456789012:role/ecsTaskRole
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3511.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_invalid_role_arn() {
        let yaml = br#"
Resources:
  Task:
    Type: AWS::ECS::TaskDefinition
    Properties:
      ExecutionRoleArn: not-an-arn
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3511.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3511"));
        assert!(issues[0].message.contains("not-an-arn"));
    }
}

crate::register_cfn_lint_rule!(E3511);
