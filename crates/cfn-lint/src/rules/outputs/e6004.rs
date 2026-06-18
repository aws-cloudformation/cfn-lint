use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E6004: Outputs have required properties.
///
/// Each output must have a 'Value' property and only allowed keys.
/// Now handled by the parent schema rule (E6001) via additionalProperties.
pub struct E6004;

impl CfnLintRule for E6004 {
    fn id(&self) -> &str {
        "E6004"
    }
    fn short_description(&self) -> &str {
        "Outputs have required properties"
    }
    fn description(&self) -> &str {
        "Making sure the outputs have required properties and no extra keys"
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

crate::register_cfn_lint_rule!(E6004);
