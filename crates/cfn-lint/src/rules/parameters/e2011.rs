use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E2011: Validate the name for a parameter.
///
/// Parameter names must not exceed 255 characters.
/// Now handled by the parent schema rule (E2001) via propertyNames.
pub struct E2011;

impl CfnLintRule for E2011 {
    fn id(&self) -> &str { "E2011" }
    fn short_description(&self) -> &str { "Validate the name for a parameter" }
    fn description(&self) -> &str {
        "Validate the name of a parameter with special handling of the max length"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(E2011);
