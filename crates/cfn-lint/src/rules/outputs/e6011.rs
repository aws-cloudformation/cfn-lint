use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E6011: Check property names in Outputs.
///
/// Output logical IDs must not exceed 255 characters.
/// Now handled by the parent schema rule (E6001) via propertyNames.
pub struct E6011;

impl CfnLintRule for E6011 {
    fn id(&self) -> &str {
        "E6011"
    }
    fn short_description(&self) -> &str {
        "Check property names in Outputs"
    }
    fn description(&self) -> &str {
        "Validate output logical IDs do not exceed the maximum length"
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

crate::register_cfn_lint_rule!(E6011);
