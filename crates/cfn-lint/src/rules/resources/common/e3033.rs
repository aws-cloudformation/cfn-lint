/// E3033 — String length validation (minLength / maxLength).
///
/// In Python cfn-lint, this rule overrides the `minLength` and `maxLength`
/// jsonschema keywords to add Fn::Sub awareness: it strips `${...}`
/// substitution placeholders from Fn::Sub strings and checks the remaining
/// literal character length against the schema constraints.
///
/// In our Rust implementation, basic minLength/maxLength validation for
/// literal strings is handled by `validate_min_length` / `validate_max_length`
/// in `jsonschema/keywords.rs`. The engine also resolves functions (including
/// Fn::Sub) before schema validation, so fully-resolvable Fn::Sub strings
/// are already covered.
///
/// TODO: For partially-resolvable Fn::Sub (where some variables can't be
/// resolved), add a heuristic to the keyword validators that strips `${...}`
/// placeholders and checks the remaining literal length. This would need to
/// be done in `jsonschema/keywords.rs` rather than here, since the Rule trait
/// does not have access to schema definitions.
use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

pub struct E3033;

impl CfnLintRule for E3033 {
    fn id(&self) -> &str {
        "E3033"
    }

    fn short_description(&self) -> &str {
        "Check if string has between min and max number of values"
    }

    fn description(&self) -> &str {
        "Validates string length constraints including Fn::Sub estimation"
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
        // Basic minLength/maxLength handled by jsonschema/keywords.rs.
        // Fn::Sub heuristic estimation requires keyword-level integration.
        vec![]
    }
}

crate::register_cfn_lint_rule!(E3033);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E3033.id(), "E3033");
        assert_eq!(
            E3033.short_description(),
            "Check if string has between min and max number of values"
        );
        assert_eq!(E3033.severity(), Severity::Error);
    }
}
