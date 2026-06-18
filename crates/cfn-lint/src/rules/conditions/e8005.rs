use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E8005: Check Fn::Not structure for validity.
/// Fn::Not must be an array of exactly 1 element.
pub struct E8005;

impl CfnLintRule for E8005 {
    fn id(&self) -> &str {
        "E8005"
    }

    fn short_description(&self) -> &str {
        "Check Fn::Not structure for validity"
    }

    fn description(&self) -> &str {
        "Check Fn::Not is a list of one element"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Validation is handled by the engine's validate_condition_functions
                vec![]
    }
}

crate::register_cfn_lint_rule!(E8005);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_validate_is_stub() {
        // Validation is handled by the engine's validate_condition_functions;
        // this rule struct is only a metadata holder for the rule registry.
        let yaml = br#"
Conditions:
  Bad:
    Fn::Not:
      - Fn::Equals:
          - a
          - b
      - Fn::Equals:
          - c
          - d
Resources:
  B:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E8005.validate_template(&tmpl, &ast).is_empty());
    }
}
