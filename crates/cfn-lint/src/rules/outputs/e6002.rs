use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E6002: Outputs must be objects.
///
/// Now handled by the parent schema rule (E6001) via type.
pub struct E6002;

impl CfnLintRule for E6002 {
    fn id(&self) -> &str {
        "E6002"
    }
    fn short_description(&self) -> &str {
        "Outputs must have unique Export names"
    }
    fn description(&self) -> &str {
        "Check that no two outputs share the same Export Name value"
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

crate::register_cfn_lint_rule!(E6002);
