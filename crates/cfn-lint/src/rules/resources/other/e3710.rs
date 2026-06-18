use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E3710: Resource type is from a service that has been shut down.
///
/// Checks if a resource type belongs to an AWS service that has reached
/// full shutdown and is no longer available. Uses the LmbdRuntimeLifecycle
/// additional spec data to identify shutdown services.
pub struct E3710;

impl CfnLintRule for E3710 {
    fn id(&self) -> &str { "E3710" }
    fn short_description(&self) -> &str { "Resource type is from a shut down service" }
    fn description(&self) -> &str {
        "Checks if a resource type belongs to an AWS service that has \
         reached full shutdown and is no longer available"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            for prefix in SHUTDOWN_PREFIXES {
                if resource.resource_type.starts_with(prefix) {
                    let span = root.get("Resources")
                        .and_then(|r| r.get(name))
                        .and_then(|r| r.get("Type"))
                        .map(|t| t.span())
                        .unwrap_or_default();
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!(
                            "Resource type '{}' is from a service that has been shut down",
                            resource.resource_type
                        ),
                        path: vec!["Resources".to_string(), name.clone(), "Type".to_string()],
                        span,
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

const SHUTDOWN_PREFIXES: &[&str] = &[
    "AWS::OpsWorks::",
    "AWS::Cloud9::",
];

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_resource_type() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3710.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_shutdown_service() {
        let yaml = br#"
Resources:
  Stack:
    Type: AWS::OpsWorks::Stack
    Properties:
      Name: test
      ServiceRoleArn: arn:aws:iam::123456789012:role/role
      DefaultInstanceProfileArn: arn:aws:iam::123456789012:instance-profile/profile
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3710.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3710"));
        assert!(issues[0].message.contains("shut down"));
    }
}

crate::register_cfn_lint_rule!(E3710);
