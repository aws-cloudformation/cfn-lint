use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E6003: Check the type of Outputs.
///
/// Each output in the Outputs section must be an object.
/// Now handled by the parent schema rule (E6001) via required.
pub struct E6003;

impl CfnLintRule for E6003 {
    fn id(&self) -> &str { "E6003" }
    fn short_description(&self) -> &str { "Check the type of Outputs" }
    fn description(&self) -> &str {
        "Check that each output in the Outputs section is an object"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(E6003);
