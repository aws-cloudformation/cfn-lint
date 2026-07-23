use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// E6003: Check the type of Outputs.
///
/// Each output in the Outputs section must be an object.
/// Now handled by the parent schema rule (E6001) via the `type` keyword,
/// matching Python cfn-lint's E6003 ("Check the type of Outputs").
pub struct E6003;

impl CfnLintRule for E6003 {
    fn id(&self) -> &str {
        "E6003"
    }
    fn short_description(&self) -> &str {
        "Check the type of Outputs"
    }
    fn description(&self) -> &str {
        "Validate the type of properties in the Outputs section"
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

crate::register_cfn_lint_rule!(E6003);
