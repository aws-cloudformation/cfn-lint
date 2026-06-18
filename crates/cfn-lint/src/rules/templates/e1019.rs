use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E1019: Validate Fn::Sub variable references across the entire template.
///
/// NOTE: This is a metadata-only stub for rule listing / --list-rules output.
/// Actual validation is performed by the schema pipeline's `fn_sub` keyword handler
/// (in `jsonschema/keywords/functions.rs`) which labels structure errors as "E1019".
pub struct E1019;

impl CfnLintRule for E1019 {
    fn id(&self) -> &str {
        "E1019"
    }

    fn short_description(&self) -> &str {
        "Fn::Sub variable references"
    }

    fn description(&self) -> &str {
        "Validate Fn::Sub variable references point to valid targets"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        // Root keyword ensures this rule appears in the registry for metadata purposes.
        // No actual dispatch occurs because validate_template returns empty.
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        _root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        // Validation is handled by the schema pipeline's fn_sub keyword (maps to "E1019")
        vec![]
    }
}

crate::register_cfn_lint_rule!(E1019);
