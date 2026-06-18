use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3020: Validate that when a property is specified another should be excluded.
///
/// Schema-driven anchor. The actual `dependentExcluded` keyword validation is
/// handled by the schema validator.
pub struct E3020;

impl CfnLintRule for E3020 {
    fn id(&self) -> &str {
        "E3020"
    }

    fn short_description(&self) -> &str {
        "Validate that when a property is specified another property should be excluded"
    }

    fn description(&self) -> &str {
        "When certain properties are specified other properties should not be included"
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

crate::register_cfn_lint_rule!(E3020);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(E3020.id(), "E3020");
        assert_eq!(E3020.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let yaml = b"Resources:\n  B:\n    Type: AWS::S3::Bucket\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3020.validate_template(&tmpl, &ast).is_empty());
    }
}
