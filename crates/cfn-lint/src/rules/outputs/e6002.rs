use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// E6002: Outputs have required properties.
///
/// Now handled by the parent schema rule (E6001) via the `required` keyword,
/// matching Python cfn-lint's E6002 ("Outputs have required properties").
pub struct E6002;

impl CfnLintRule for E6002 {
    fn id(&self) -> &str {
        "E6002"
    }
    fn short_description(&self) -> &str {
        "Outputs have required properties"
    }
    fn description(&self) -> &str {
        "Making sure the outputs have required properties"
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
