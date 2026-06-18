use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;

/// E1033: Validate Fn::GetStackOutput configuration.
///
/// Validation is performed by the `fn_getstackoutput` keyword validator
/// in the schema engine. This rule struct provides metadata and registration.
pub struct E1033;

impl CfnLintRule for E1033 {
    fn id(&self) -> &str { "E1033" }
    fn short_description(&self) -> &str { "Validate GetStackOutput configuration" }
    fn description(&self) -> &str { "Validates that Fn::GetStackOutput has the correct structure with required StackName and OutputName fields" }
    fn severity(&self) -> Severity { Severity::Error }
    fn keywords(&self) -> &[&str] { &[] }
}

crate::register_cfn_lint_rule!(E1033);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E1033.id(), "E1033");
        assert_eq!(E1033.severity(), Severity::Error);
    }
}
