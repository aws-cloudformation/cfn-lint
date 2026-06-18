use crate::ast::{self, AstNode};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

pub struct E1032;

fn has_language_extensions(root: &AstNode) -> bool {
    match root.get("Transform") {
        Some(AstNode::String(s)) => s.value == "AWS::LanguageExtensions",
        Some(AstNode::Array(arr)) => arr
            .elements
            .iter()
            .any(|e| e.as_str() == Some("AWS::LanguageExtensions")),
        _ => false,
    }
}

impl CfnLintRule for E1032 {
    fn id(&self) -> &str {
        "E1032"
    }

    fn short_description(&self) -> &str {
        "Validates ForEach functions"
    }

    fn description(&self) -> &str {
        "Validates that Fn::ForEach parameters have a valid configuration"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let has_ext = has_language_extensions(root);
        let mut issues = Vec::new();

        // Fn::ForEach is used as object keys like "Fn::ForEach::UniqueId"
        // and also as a FunctionNode when parsed via !ForEach tag
        ast::walk(root, &[], &mut |node, path| {
            // Check for Fn::ForEach as a FunctionNode (from !ForEach tag)
            if let AstNode::Function(func) = node {
                if func.name == "Fn::ForEach" {
                    if !has_ext {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: "Missing Transform: Declare the AWS::LanguageExtensions Transform globally to enable use of Fn::ForEach".to_string(),
                            path: path.to_vec(),
                            span: func.span.clone(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                        schema_id: None,
                        });
                        return false;
                    }
                    match func.args.as_ref() {
                        AstNode::Array(arr) if arr.elements.len() == 3 => {
                            if !matches!(&arr.elements[0], AstNode::String(_)) {
                                issues.push(ValidationError {
                                    rule_id: Some(self.id().to_string()),
                                    message: "Fn::ForEach first element must be a string identifier".to_string(),
                                    path: path.to_vec(),
                                    span: func.span.clone(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                                schema_id: None,
                                });
                            }
                        }
                        AstNode::Function(_) => {}
                        _ => {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: "Fn::ForEach must be a 3-element array [identifier, collection, body]".to_string(),
                                path: path.to_vec(),
                                span: func.span.clone(),
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

            // Check for Fn::ForEach::* as object keys
            if let AstNode::Object(obj) = node {
                for (key, value) in obj.iter() {
                    if key.starts_with("Fn::ForEach::") {
                        let mut key_path = path.to_vec();
                        key_path.push(key.to_string());
                        if !has_ext {
                            issues.push(ValidationError {
                                rule_id: Some(self.id().to_string()),
                                message: "Missing Transform: Declare the AWS::LanguageExtensions Transform globally to enable use of Fn::ForEach".to_string(),
                                path: key_path,
                                span: value.span().clone(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                            schema_id: None,
                            });
                        } else if let AstNode::Array(arr) = value {
                            if arr.elements.len() != 3 {
                                issues.push(ValidationError {
                                    rule_id: Some(self.id().to_string()),
                                    message: "Fn::ForEach must be a 3-element array [identifier, collection, body]".to_string(),
                                    path: key_path,
                                    span: arr.span.clone(),
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
            true
        });
        issues
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_foreach_with_transform() {
        let yaml = br#"
Transform: AWS::LanguageExtensions
Resources:
  Fn::ForEach::Loop:
    - Identifier
    - - a
      - b
    - Resource${Identifier}:
        Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E1032.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_foreach_without_transform() {
        let yaml = br#"
Resources:
  Fn::ForEach::Loop:
    - Identifier
    - - a
      - b
    - Resource${Identifier}:
        Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1032.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E1032"));
        assert!(issues[0].message.contains("LanguageExtensions"));
    }
}

crate::register_cfn_lint_rule!(E1032);
