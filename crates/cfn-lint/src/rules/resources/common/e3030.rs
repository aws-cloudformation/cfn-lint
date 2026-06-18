use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E3030: Check if properties have a valid value.
///
/// Schema-driven anchor. The actual `enum` keyword validation is
/// handled by the schema validator and mapped to this rule ID.
pub struct E3030;

impl CfnLintRule for E3030 {
    fn id(&self) -> &str {
        "E3030"
    }

    fn short_description(&self) -> &str {
        "Check if properties have a valid value"
    }

    fn description(&self) -> &str {
        "Validates property values match allowed enum values from the schema"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(E3030);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(E3030.id(), "E3030");
        assert_eq!(E3030.severity(), Severity::Error);
    }

    #[test]
    fn test_anchor_returns_empty() {
        let yaml = b"Resources:\n  B:\n    Type: AWS::S3::Bucket\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3030.validate_template(&tmpl, &ast).is_empty());
    }
}
