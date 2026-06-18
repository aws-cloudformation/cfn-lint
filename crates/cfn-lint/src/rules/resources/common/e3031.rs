use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E3031 — Validates that string values match their declared AWS format
/// (e.g. AMI IDs, Security Group IDs, VPC IDs).
///
/// Actual validation is performed by the `format` keyword in the JSON Schema
/// validator. This rule serves as the rule-ID anchor so that format errors
/// can be suppressed via `ignore_checks: [E3031]`.
pub struct E3031;

impl CfnLintRule for E3031 {
    fn id(&self) -> &str {
        "E3031"
    }

    fn short_description(&self) -> &str {
        "Check resource property format"
    }

    fn description(&self) -> &str {
        "Validates that string values match their declared AWS format (e.g. AMI IDs, VPC IDs)"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Format validation is handled by the jsonschema format keyword validator.
                // Schema errors with keyword "format" are mapped to rule E3031 in the engine.
                vec![]
    }
}

crate::register_cfn_lint_rule!(E3031);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_e3031_metadata() {
        assert_eq!(E3031.id(), "E3031");
        assert_eq!(E3031.severity(), Severity::Error);
    }

    #[test]
    fn test_e3031_validate_returns_empty() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3031.validate_template(&tmpl, &ast).is_empty());
    }
}
