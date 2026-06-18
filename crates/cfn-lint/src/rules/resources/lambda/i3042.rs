use regex::Regex;

use crate::ast::{self, AstNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// I3042: ARNs should use correctly placed Pseudo Parameters.
///
/// Walks all resource properties looking for strings inside `Fn::Sub` that
/// contain ARNs with a hardcoded partition (the first field after `arn:`).
/// A partition is considered hardcoded when it is not a `${...}` variable
/// reference, `*`, or empty.
pub struct I3042;

impl CfnLintRule for I3042 {
    fn id(&self) -> &str {
        "I3042"
    }
    fn short_description(&self) -> &str {
        "ARNs should use correctly placed Pseudo Parameters"
    }
    fn description(&self) -> &str {
        "Checks Resources if ARNs use correctly placed Pseudo Parameters instead of hardcoded Partition, Region, and Account Number"
    }
    fn severity(&self) -> Severity {
        Severity::Informational
    }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let arn_re = Regex::new(
            r"arn:(\$\{[^:\r\n]*::[^:\r\n]*}|[^:\s]*):[^:\s]+:(\$\{[^:\r\n]*::[^:\r\n]*}|[^:\s]*):(\$\{[^:\r\n]*::[^:\r\n]*}|[^:\s]*)"
        ).unwrap();

        let resources = match root.get("Resources") {
            Some(r) => r,
            None => return vec![],
        };

        let mut issues = Vec::new();

        ast::walk(resources, &["Resources".to_string()], &mut |node, path| {
            if let AstNode::Function(func) = node {
                if func.name == "Fn::Sub" {
                    let tmpl_str = match func.args.as_ref() {
                        AstNode::String(s) => Some(s.value.as_str()),
                        AstNode::Array(arr) if !arr.elements.is_empty() => {
                            arr.elements[0].as_str()
                        }
                        _ => None,
                    };

                    if let Some(s) = tmpl_str {
                        for caps in arn_re.captures_iter(s) {
                            let partition = caps.get(1).map_or("", |m| m.as_str());
                            if !partition_ok(partition) {
                                let resource_name = path
                                    .get(1)
                                    .map(|s| s.as_str())
                                    .unwrap_or("Unknown");

                                let mut issue_path = path.to_vec();
                                issue_path.push(func.name.clone());

                                issues.push(ValidationError {
                                    rule_id: Some(self.id().to_string()),
                                    message: format!(
                                        "ARN in Resource {} contains hardcoded Partition in ARN or incorrectly placed Pseudo Parameters",
                                        resource_name
                                    ),
                                    path: issue_path,
                                    span: func.span.clone(),
                                    keyword: String::new(),
                                    unknown: false,
                                    resolved_from_ref: false,
                                    context: vec![],
                                    schema_id: None,
});
                                break;
                            }
                        }
                    }
                }
            }
            true
        });

        issues
    }
}

/// Returns true if the partition value is acceptable (not hardcoded).
fn partition_ok(partition: &str) -> bool {
    partition.is_empty()
        || partition == "*"
        || partition.starts_with("${")
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_hardcoded_partition_flagged() {
        let yaml = br#"
Resources:
  MyFunc:
    Type: AWS::Lambda::Function
    Properties:
      Role: !Sub "arn:aws:iam::${AWS::AccountId}:role/my-role"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = I3042.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("I3042"));
        assert!(issues[0].message.contains("MyFunc"));
        assert!(issues[0].message.contains("hardcoded Partition"));
    }

    #[test]
    fn test_pseudo_partition_no_issue() {
        let yaml = br#"
Resources:
  MyFunc:
    Type: AWS::Lambda::Function
    Properties:
      Role: !Sub "arn:${AWS::Partition}:iam::${AWS::AccountId}:role/my-role"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I3042.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(I3042);
