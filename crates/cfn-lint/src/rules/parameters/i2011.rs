use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// I2011: Parameter name limit.
///
/// Now handled by the parent schema rule via child-rule mapping.
pub struct I2011;

impl CfnLintRule for I2011 {
    fn id(&self) -> &str { "I2011" }
    fn short_description(&self) -> &str { "Parameter name limit" }
    fn description(&self) -> &str {
        "Check the size of Parameter names in the template is approaching the upper limit"
    }
    fn severity(&self) -> Severity { Severity::Informational }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(I2011);
