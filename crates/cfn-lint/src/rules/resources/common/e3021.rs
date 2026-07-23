use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// E3021: Validate that when a property is specified other properties should be included.
///
/// Schema-driven anchor. The actual `dependentRequired` keyword validation is
/// handled by the schema validator.
pub struct E3021;

impl CfnLintRule for E3021 {
    fn id(&self) -> &str {
        "E3021"
    }

    fn short_description(&self) -> &str {
        "Validate that when a property is specified other properties should be included"
    }

    fn description(&self) -> &str {
        "When certain properties are specified it results in other properties to be required"
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

crate::register_cfn_lint_rule!(E3021);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(E3021.id(), "E3021");
        assert_eq!(E3021.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let yaml = b"Resources:\n  B:\n    Type: AWS::S3::Bucket\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3021.validate_template(&tmpl, &ast).is_empty());
    }
}
