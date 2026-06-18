use crate::ast::{self, AstNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// I1022: Prefer `Fn::Sub` over `Fn::Join` when the delimiter is empty.
///
/// When `Fn::Join` is called with an empty string delimiter and all elements
/// are simple references (Ref, Fn::GetAtt, or Fn::Sub with a string value),
/// `Fn::Sub` is the idiomatic replacement.
pub struct I1022;

impl CfnLintRule for I1022 {
    fn id(&self) -> &str {
        "I1022"
    }
    fn short_description(&self) -> &str {
        "Use Sub instead of Join"
    }
    fn description(&self) -> &str {
        "Prefer a sub instead of Join when using a join delimiter that is empty"
    }
    fn severity(&self) -> Severity {
        Severity::Informational
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let mut issues = Vec::new();
        ast::walk(root, &[], &mut |node, path| {
            if let AstNode::Function(func) = node {
                if func.name == "Fn::Join" {
                    if let AstNode::Array(arr) = func.args.as_ref() {
                        if arr.elements.len() == 2 {
                            // Check first element is empty string delimiter
                            if let Some(delim) = arr.elements[0].as_str() {
                                if delim.is_empty() && check_elements(&arr.elements[1]) {
                                    let mut issue_path = path.to_vec();
                                    issue_path.push("Fn::Join".to_string());
                                    issue_path.push("0".to_string());
                                    issues.push(ValidationError {
                                        rule_id: Some(self.id().to_string()),
                                        message: "Prefer using Fn::Sub over Fn::Join with an empty delimiter".to_string(),
                                        path: issue_path,
                                        span: func.span,
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
                }
            }
            true
        });
        issues
    }
}

/// Check that all elements in the join list are simple references that can be
/// trivially converted to `Fn::Sub` syntax: Ref, Fn::GetAtt, plain strings,
/// or Fn::Sub with a string (not array) argument.
fn check_elements(node: &AstNode) -> bool {
    let arr = match node {
        AstNode::Array(a) => a,
        _ => return false,
    };
    for elem in &arr.elements {
        if !check_element(elem) {
            return false;
        }
    }
    true
}

/// Check that a single element is simple enough for Sub conversion.
fn check_element(node: &AstNode) -> bool {
    match node {
        AstNode::Function(func) => {
            match func.name.as_str() {
                "Ref" | "Fn::GetAtt" => true,
                "Fn::Sub" => {
                    // Only simple string Sub is acceptable
                    matches!(func.args.as_ref(), AstNode::String(_))
                }
                _ => false,
            }
        }
        AstNode::Object(obj) => {
            // Single-key dict that is a function
            if obj.len() == 1 {
                let key = obj.keys().next().unwrap_or("");
                match key {
                    "Ref" | "Fn::GetAtt" => true,
                    "Fn::Sub" => {
                        if let Some(v) = obj.get(key) {
                            matches!(v, AstNode::String(_))
                        } else {
                            false
                        }
                    }
                    _ => false,
                }
            } else {
                false
            }
        }
        // Plain strings and other scalars are fine
        _ => true,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_empty_delimiter_simple_refs() {
        let yaml = br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Join:
          - ""
          - - !Ref AWS::StackName
            - "-bucket"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = I1022.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("I1022"));
        assert_eq!(issues[0].rule_id.as_deref(), Some("I1022"));
        assert!(issues[0].message.contains("Fn::Sub"));
    }

    #[test]
    fn test_non_empty_delimiter_no_issue() {
        let yaml = br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Join:
          - "-"
          - - !Ref AWS::StackName
            - "bucket"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I1022.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_complex_element_no_issue() {
        let yaml = br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Join:
          - ""
          - - !Ref AWS::StackName
            - Fn::Select:
                - 0
                - !Split ["-", "a-b"]
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I1022.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_no_join_no_issue() {
        let yaml = br#"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I1022.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(I1022);
