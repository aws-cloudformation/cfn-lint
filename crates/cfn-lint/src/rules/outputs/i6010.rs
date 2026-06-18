use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// I6010: Output limit approaching.
///
/// Now handled by the parent schema rule via child-rule mapping.
pub struct I6010;

impl CfnLintRule for I6010 {
    fn id(&self) -> &str { "I6010" }
    fn short_description(&self) -> &str { "Output limit" }
    fn description(&self) -> &str {
        "Check the number of Outputs in the template is approaching the upper limit"
    }
    fn severity(&self) -> Severity { Severity::Informational }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(I6010);
