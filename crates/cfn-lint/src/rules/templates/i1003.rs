use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct I1003;

impl CfnLintRule for I1003 {
    fn id(&self) -> &str {
        "I1003"
    }
    fn short_description(&self) -> &str {
        "Validate if we are approaching the max size of a description"
    }
    fn description(&self) -> &str {
        "Check if the template description is approaching the 1024 character limit"
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
        if let Some(AstNode::String(desc)) = root.get("Description") {
            if desc.value.len() > 921 {
                return vec![ValidationError {
                    rule_id: Some(self.id().to_string()),
                    message: format!(
                        "Template description is approaching the 1024 character limit (current: {})",
                        desc.value.len()
                    ),
                    path: vec!["Description".to_string()],
                    span: desc.span,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
}];
            }
        }
        vec![]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_short_description_ok() {
        let yaml = b"Description: short\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I1003.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_description_over_921() {
        let long = "x".repeat(922);
        let yaml = format!("Description: '{}'\n", long);
        let ast = parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = I1003.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("I1003"));
        assert_eq!(issues[0].rule_id.as_deref(), Some("I1003"));
    }

    #[test]
    fn test_description_exactly_921() {
        let desc = "x".repeat(921);
        let yaml = format!("Description: '{}'\n", desc);
        let ast = parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I1003.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_no_description() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I1003.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(I1003);
