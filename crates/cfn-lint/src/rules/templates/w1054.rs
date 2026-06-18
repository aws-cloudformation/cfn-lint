use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// W1054: Pseudo-parameter string found without Ref
pub struct W1054;

const PSEUDO_PARAMS: &[&str] = &[
    "AWS::AccountId",
    "AWS::NotificationARNs",
    "AWS::NoValue",
    "AWS::Partition",
    "AWS::Region",
    "AWS::StackId",
    "AWS::StackName",
    "AWS::URLSuffix",
];

impl W1054 {
    fn check_node(&self, node: &AstNode, path: &[String], issues: &mut Vec<ValidationError>) {
        match node {
            AstNode::Function(func) => {
                // Don't flag strings inside Ref — that's the correct usage
                if func.name == "Ref" {
                    return;
                }
                self.check_node(&func.args, path, issues);
            }
            AstNode::String(s) => {
                if !PSEUDO_PARAMS.contains(&s.value.as_str()) {
                    return;
                }
                // Skip resource Type field
                if path.last().map_or(false, |p| p == "Type")
                    && path.first().map_or(false, |p| p == "Resources")
                    && path.len() == 3
                {
                    return;
                }
                issues.push(ValidationError {
                    rule_id: Some("W1054".to_string()),
                    message: format!(
                        "{:?} is a pseudo-parameter and should probably be used as \
                         'Ref: {}' instead of a plain string",
                        s.value, s.value
                    ),
                    path: path.to_vec(),
                    span: s.span,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
});
            }
            AstNode::Object(obj) => {
                for (key, value) in obj.iter() {
                    let mut child_path = path.to_vec();
                    child_path.push(key.to_string());
                    self.check_node(value, &child_path, issues);
                }
            }
            AstNode::Array(arr) => {
                for (i, elem) in arr.elements.iter().enumerate() {
                    let mut child_path = path.to_vec();
                    child_path.push(i.to_string());
                    self.check_node(elem, &child_path, issues);
                }
            }
            _ => {}
        }
    }
}

impl CfnLintRule for W1054 {
    fn id(&self) -> &str { "W1054" }
    fn short_description(&self) -> &str {
        "Pseudo-parameter string found without Ref"
    }
    fn description(&self) -> &str {
        "A pseudo-parameter such as 'AWS::Region' was used as a plain string value. \
         In most cases you want 'Ref: AWS::...' instead of the raw string."
    }
    fn severity(&self) -> Severity { Severity::Warning }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let mut issues = Vec::new();
        // Only check within Resources (matches Python which fires via schema validation)
        if let Some(resources) = root.get("Resources") {
            self.check_node(resources, &["Resources".to_string()], &mut issues);
        }
        issues
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_raw_pseudo_param_flagged() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: AWS::Region
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = W1054.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.contains("AWS::Region"));
    }

    #[test]
    fn test_ref_pseudo_param_not_flagged() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref AWS::Region
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1054.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_resource_type_not_flagged() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1054.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W1054);
