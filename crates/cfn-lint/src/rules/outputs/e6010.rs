use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E6010: Output limit not exceeded.
///
/// CloudFormation templates are limited to 200 outputs.
/// Now handled by the parent schema rule (E6001) via maxProperties.
pub struct E6010;

impl CfnLintRule for E6010 {
    fn id(&self) -> &str { "E6010" }
    fn short_description(&self) -> &str { "Output limit not exceeded" }
    fn description(&self) -> &str {
        "Check the number of Outputs in the template is less than the upper limit"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(E6010);
