use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E3016;

const UPDATE_POLICY_RESOURCE_TYPES: &[&str] = &[
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::ElastiCache::ReplicationGroup",
    "AWS::OpenSearchService::Domain",
    "AWS::Elasticsearch::Domain",
    "AWS::Lambda::Alias",
    "AWS::AppStream::Fleet",
];

impl CfnLintRule for E3016 {
    fn id(&self) -> &str {
        "E3016"
    }

    fn short_description(&self) -> &str {
        "Check the configuration of a resources UpdatePolicy"
    }

    fn description(&self) -> &str {
        "Validates the UpdatePolicy configuration of resources"
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
        let resources = match root.get("Resources").and_then(|r| r.as_object()) {
            Some(r) => r,
            None => return issues,
        };

        for (name, resource_node) in resources.iter() {
            let resource_obj = match resource_node.as_object() {
                Some(o) => o,
                None => continue,
            };

            let update_policy = match resource_obj.get("UpdatePolicy") {
                Some(up) => up,
                None => continue,
            };

            let res_type = match template.resources.get(name) {
                Some(r) => r.resource_type.as_str(),
                None => continue,
            };

            // Check if UpdatePolicy is on a supported resource type
            if !UPDATE_POLICY_RESOURCE_TYPES.contains(&res_type) {
                issues.push(ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "UpdatePolicy is not supported for resource type '{}'",
                        res_type
                    ),
                    path: vec!["Resources".into(), name.to_string(), "UpdatePolicy".into()],
                    span: update_policy.span().clone(),
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
                continue;
            }

            // Validate UpdatePolicy is an object (skip functions)
            if update_policy.as_function().is_some() {
                continue;
            }
            if update_policy.as_object().is_none() {
                issues.push(ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: "UpdatePolicy must be an object".to_string(),
                    path: vec!["Resources".into(), name.to_string(), "UpdatePolicy".into()],
                    span: update_policy.span().clone(),
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_update_policy_on_asg() {
        let yaml = br#"
Resources:
  ASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    UpdatePolicy:
      AutoScalingRollingUpdate:
        MaxBatchSize: 1
    Properties:
      MinSize: "1"
      MaxSize: "4"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3016.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_update_policy_on_unsupported_type() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    UpdatePolicy:
      AutoScalingRollingUpdate:
        MaxBatchSize: 1
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3016.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("not supported"));
        assert!(issues[0].message.contains("AWS::S3::Bucket"));
    }

    #[test]
    fn test_update_policy_not_object() {
        let yaml = br#"
Resources:
  ASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    UpdatePolicy: "invalid"
    Properties:
      MinSize: "1"
      MaxSize: "4"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3016.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("must be an object"));
    }

    #[test]
    fn test_no_update_policy_no_issues() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3016.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3016);
