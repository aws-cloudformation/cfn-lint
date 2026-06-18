use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// I7002: Mapping name approaching max length.
///
/// Now handled by the parent schema rule via child-rule mapping.
pub struct I7002;

impl CfnLintRule for I7002 {
    fn id(&self) -> &str { "I7002" }
    fn short_description(&self) -> &str { "Mapping name limit" }
    fn description(&self) -> &str {
        "Check the size of Mapping names in the template is approaching the upper limit"
    }
    fn severity(&self) -> Severity { Severity::Informational }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(I7002);
