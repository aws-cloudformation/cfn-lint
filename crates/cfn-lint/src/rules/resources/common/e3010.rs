use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E3010: Resource limit not exceeded.
///
/// Produced by E3001 when the Resources section schema's maxProperties
/// constraint fires. This rule exists for metadata (--list-rules, --ignore-checks).
pub struct E3010;

impl CfnLintRule for E3010 {
    fn id(&self) -> &str {
        "E3010"
    }
    fn short_description(&self) -> &str {
        "Resource limit not exceeded"
    }
    fn description(&self) -> &str {
        "Check the number of Resources in the template is less than the upper limit"
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
        // Handled by E3001 schema validation (maxProperties → E3010)
        vec![]
    }
}

crate::register_cfn_lint_rule!(E3010);
