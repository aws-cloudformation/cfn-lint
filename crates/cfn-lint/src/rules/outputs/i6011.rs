use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// I6011: Output name approaching max length.
///
/// Now handled by the parent schema rule via child-rule mapping.
pub struct I6011;

impl CfnLintRule for I6011 {
    fn id(&self) -> &str {
        "I6011"
    }
    fn short_description(&self) -> &str {
        "Output name limit"
    }
    fn description(&self) -> &str {
        "Check the size of Output names in the template is approaching the upper limit"
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
        _root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(I6011);
