use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E2010: Parameter limit not exceeded.
///
/// Now handled by the parent schema rule (E2001) via maxProperties.
pub struct E2010;

impl CfnLintRule for E2010 {
    fn id(&self) -> &str { "E2010" }
    fn short_description(&self) -> &str { "Parameter limit not exceeded" }
    fn description(&self) -> &str {
        "Check the number of Parameters in the template is less than the upper limit"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(E2010);
