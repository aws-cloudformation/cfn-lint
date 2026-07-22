use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// E0100: Validate deployment file configuration.
///
/// Validates that a deployment file has the correct syntax for one of
/// the supported formats. This is a structural validation rule.
pub struct E0100;

impl CfnLintRule for E0100 {
    fn id(&self) -> &str {
        "E0100"
    }

    fn short_description(&self) -> &str {
        "Validate deployment file configuration"
    }

    fn description(&self) -> &str {
        "Validate deployment file configuration"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        _root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        // Deployment file validation is handled at the runner level
        // before template parsing. This rule serves as a registry anchor.
        vec![]
    }
}

crate::register_cfn_lint_rule!(E0100);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E0100.id(), "E0100");
        assert_eq!(E0100.severity(), Severity::Error);
    }

    #[test]
    fn test_returns_empty() {
        let yaml = br#"
AWSTemplateFormatVersion: "2010-09-09"
"#;
        let ast = crate::parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E0100.validate_template(&tmpl, &ast).is_empty());
    }
}
