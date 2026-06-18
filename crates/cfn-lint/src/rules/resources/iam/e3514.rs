use regex::Regex;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E3514: Validate IAM resource policy resource ARNs.
///
/// Validates that Resource ARNs in IAM policy statements match a compliant
/// ARN pattern. For S3::BucketPolicy, the wildcard-only `*` is not allowed.
pub struct E3514;

impl CfnLintRule for E3514 {
    fn id(&self) -> &str {
        "E3514"
    }
    fn short_description(&self) -> &str {
        "Validate IAM resource policy resource ARNs"
    }
    fn description(&self) -> &str {
        "Validates an IAM resource policy has a compliant resource ARN"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let re = match Regex::new(RESOURCE_ARN_PATTERN) {
            Ok(r) => r,
            Err(_) => return vec![],
        };
        let s3_re = match Regex::new(S3_RESOURCE_ARN_PATTERN) {
            Ok(r) => r,
            Err(_) => return vec![],
        };
        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            if !POLICY_RESOURCE_TYPES.contains(&resource.resource_type.as_str()) {
                continue;
            }
            let props = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };
            let is_s3 = resource.resource_type == "AWS::S3::BucketPolicy";
            let pattern = if is_s3 { &s3_re } else { &re };

            // Find PolicyDocument in various locations
            let policy_doc = props.get("PolicyDocument")
                .or_else(|| props.get("PolicyText"))
                .or_else(|| props.get("KeyPolicy"))
                .or_else(|| props.get("AccessPolicies"));
            if let Some(doc) = policy_doc {
                self.check_statements(name, doc, pattern, &mut issues);
            }
        }
        issues
    }
}

const RESOURCE_ARN_PATTERN: &str =
    r"^(arn:aws[A-Za-z\-]*?:[^:]+:[^:]*(:(?:\d{12}|\*|aws)?:.+|)|\*)$";
const S3_RESOURCE_ARN_PATTERN: &str =
    r"^arn:aws[A-Za-z\-]*?:[^:]+:[^:]*(:(?:\d{12}|\*|aws)?:.+|)$";

const POLICY_RESOURCE_TYPES: &[&str] = &[
    "AWS::IAM::Policy",
    "AWS::S3::BucketPolicy",
    "AWS::SNS::TopicPolicy",
    "AWS::SQS::QueuePolicy",
    "AWS::KMS::Key",
    "AWS::OpenSearchService::Domain",
];

impl E3514 {
    fn check_statements(&self, resource_name: &str, doc: &AstNode, pattern: &Regex, issues: &mut Vec<ValidationError>) {
        let statements = match doc.get("Statement").and_then(|n| n.as_array()) {
            Some(a) => a,
            None => return,
        };
        for (i, stmt) in statements.elements.iter().enumerate() {
            if let Some(resource_node) = stmt.get("Resource") {
                self.check_resource_value(resource_name, i, resource_node, pattern, issues);
            }
        }
    }

    fn check_resource_value(
        &self,
        resource_name: &str,
        stmt_idx: usize,
        node: &AstNode,
        pattern: &Regex,
        issues: &mut Vec<ValidationError>,
    ) {
        match node {
            AstNode::String(s) => {
                // Skip strings containing ${...} patterns (IAM policy variables)
                if s.value.contains("${") {
                    return;
                }
                if !pattern.is_match(&s.value) {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!("'{}' does not match '{}'", s.value, pattern.as_str()),
                        path: vec![
                            "Resources".into(),
                            resource_name.to_string(),
                            "Properties".into(),
                            "PolicyDocument".into(),
                            "Statement".into(),
                            stmt_idx.to_string(),
                            "Resource".into(),
                        ],
                        span: s.span.clone(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
});
                }
            }
            AstNode::Array(arr) => {
                for elem in &arr.elements {
                    self.check_resource_value(resource_name, stmt_idx, elem, pattern, issues);
                }
            }
            _ => {}
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_resource_arn() {
        let yaml = br#"
Resources:
  Policy:
    Type: AWS::IAM::ManagedPolicy
    Properties:
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action: "s3:GetObject"
            Resource: "arn:aws:s3:::my-bucket/*"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3514.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_invalid_resource_arn() {
        let yaml = br#"
Resources:
  Policy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Action: "s3:GetObject"
            Resource: "not-a-valid-arn"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E3514.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E3514"));
        assert!(issues[0].message.contains("not-a-valid-arn"));
    }
}

crate::register_cfn_lint_rule!(E3514);
