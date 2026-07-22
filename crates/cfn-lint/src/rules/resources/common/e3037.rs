use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// E3037: Check if a list has duplicate values.
///
/// Schema-driven anchor. The actual `uniqueItems` keyword validation is
/// handled by the schema validator.
pub struct E3037;

impl CfnLintRule for E3037 {
    fn id(&self) -> &str {
        "E3037"
    }

    fn short_description(&self) -> &str {
        "Check if a list has duplicate values"
    }

    fn description(&self) -> &str {
        "Certain lists don't support duplicate items. Check when duplicates are provided but not supported."
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
        vec![]
    }
}

crate::register_cfn_lint_rule!(E3037);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(E3037.id(), "E3037");
        assert_eq!(E3037.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let yaml = b"Resources:\n  B:\n    Type: AWS::S3::Bucket\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3037.validate_template(&tmpl, &ast).is_empty());
    }
}
