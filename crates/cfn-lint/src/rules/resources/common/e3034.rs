use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E3034: Check if a number is between min and max.
///
/// In Python cfn-lint this hooks into the JSON Schema `minimum`, `maximum`,
/// `exclusiveMinimum`, `exclusiveMaximum` keywords. The actual validation is
/// handled by the schema validator. This struct exists as a rule ID anchor
/// for `--list-rules` and suppression metadata.
pub struct E3034;

impl CfnLintRule for E3034 {
    fn id(&self) -> &str {
        "E3034"
    }

    fn short_description(&self) -> &str {
        "Check if a number is between min and max"
    }

    fn description(&self) -> &str {
        "Check numbers (integers and floats) for its value being between the minimum and maximum"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Validation is performed by the schema validator's min/max keywords.
                vec![]
    }
}

crate::register_cfn_lint_rule!(E3034);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_anchor_returns_empty() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3034.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E3034.id(), "E3034");
        assert_eq!(E3034.severity(), Severity::Error);
    }
}
