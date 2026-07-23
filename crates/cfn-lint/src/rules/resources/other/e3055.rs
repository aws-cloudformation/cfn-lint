use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3055: Check CreationPolicy values for Resources.
///
/// Mirrors Python cfn-lint `resources/CreationPolicy.py`. Validates that
/// CreationPolicy is only used on supported resource types and that its
/// structure matches the expected schema per resource type.
pub struct E3055;

impl CfnLintRule for E3055 {
    fn id(&self) -> &str {
        "E3055"
    }
    fn short_description(&self) -> &str {
        "Check CreationPolicy values for Resources"
    }
    fn description(&self) -> &str {
        "Check that the CreationPolicy values are valid"
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

        let mut issues = Vec::new();
        for (name, node) in resources.iter() {
            let policy_node = match node.get("CreationPolicy") {
                Some(n) => n,
                None => continue,
            };

            let resource_type = template
                .resources
                .get(name)
                .map(|r| r.resource_type.as_str())
                .unwrap_or("");

            if !SUPPORTED_TYPES.contains(&resource_type) {
                // Skip MODULE resource types
                if resource_type.ends_with("::MODULE") {
                    continue;
                }
                issues.push(ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "CreationPolicy is not supported for resource type '{}'",
                        resource_type
                    ),
                    path: vec![
                        "Resources".to_string(),
                        name.to_string(),
                        "CreationPolicy".to_string(),
                    ],
                    span: policy_node.span(),
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
                continue;
            }

            let policy_obj = match policy_node.as_object() {
                Some(o) => o,
                None => continue,
            };

            let allowed_keys: &[&str] = match resource_type {
                "AWS::AppStream::Fleet" => VALID_APPSTREAM_KEYS,
                "AWS::AutoScaling::AutoScalingGroup" => VALID_ASG_KEYS,
                "AWS::CloudFormation::WaitCondition" | "AWS::EC2::Instance" => {
                    VALID_WAIT_CONDITION_KEYS
                }
                _ => continue,
            };

            for key in policy_obj.keys() {
                if !allowed_keys.contains(&key) {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!(
                            "Invalid CreationPolicy property '{}' for resource type '{}'",
                            key, resource_type
                        ),
                        path: vec![
                            "Resources".to_string(),
                            name.to_string(),
                            "CreationPolicy".to_string(),
                            key.to_string(),
                        ],
                        span: policy_obj.get(key).map(|n| n.span()).unwrap_or_default(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }

            // Validate nested AutoScalingCreationPolicy keys
            if resource_type == "AWS::AutoScaling::AutoScalingGroup" {
                if let Some(asc) = policy_obj
                    .get("AutoScalingCreationPolicy")
                    .and_then(|n| n.as_object())
                {
                    for key in asc.keys() {
                        if !VALID_ASG_CREATION_POLICY_KEYS.contains(&key) {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: format!(
                                    "Invalid AutoScalingCreationPolicy property '{}'",
                                    key
                                ),
                                path: vec![
                                    "Resources".to_string(),
                                    name.to_string(),
                                    "CreationPolicy".to_string(),
                                    "AutoScalingCreationPolicy".to_string(),
                                    key.to_string(),
                                ],
                                span: asc.get(key).map(|n| n.span()).unwrap_or_default(),
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

            // Validate nested ResourceSignal keys
            if let Some(rs) = policy_obj.get("ResourceSignal").and_then(|n| n.as_object()) {
                for key in rs.keys() {
                    if !VALID_RESOURCE_SIGNAL_KEYS.contains(&key) {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!("Invalid ResourceSignal property '{}'", key),
                            path: vec![
                                "Resources".to_string(),
                                name.to_string(),
                                "CreationPolicy".to_string(),
                                "ResourceSignal".to_string(),
                                key.to_string(),
                            ],
                            span: rs.get(key).map(|n| n.span()).unwrap_or_default(),
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

const VALID_APPSTREAM_KEYS: &[&str] = &["StartFleet"];
const VALID_ASG_KEYS: &[&str] = &["AutoScalingCreationPolicy", "ResourceSignal"];
const VALID_ASG_CREATION_POLICY_KEYS: &[&str] = &["MinSuccessfulInstancesPercent"];
const VALID_RESOURCE_SIGNAL_KEYS: &[&str] = &["Timeout", "Count"];
const VALID_WAIT_CONDITION_KEYS: &[&str] = &["ResourceSignal"];

const SUPPORTED_TYPES: &[&str] = &[
    "AWS::AppStream::Fleet",
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::CloudFormation::WaitCondition",
    "AWS::EC2::Instance",
];

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_creation_policy_asg() {
        let yaml = br#"
Resources:
  ASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    CreationPolicy:
      AutoScalingCreationPolicy:
        MinSuccessfulInstancesPercent: 80
      ResourceSignal:
        Timeout: PT15M
        Count: 3
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3055.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_unsupported_resource_type() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    CreationPolicy:
      ResourceSignal:
        Timeout: PT15M
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3055.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3055"));
        assert!(issues[0].message.contains("not supported"));
    }
}

crate::register_cfn_lint_rule!(E3055);
