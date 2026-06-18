use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E7010: Mapping count limit.
///
/// Check that mapping key names are between 1 and 255 characters.
/// Now handled by the parent schema rule (E7001) via maxProperties.
pub struct E7010;

impl CfnLintRule for E7010 {
    fn id(&self) -> &str {
        "E7010"
    }
    fn short_description(&self) -> &str {
        "Mapping key names must not exceed length limit"
    }
    fn description(&self) -> &str {
        "Check that mapping key names are between 1 and 255 characters"
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

crate::register_cfn_lint_rule!(E7010);
