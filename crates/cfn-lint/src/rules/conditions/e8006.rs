use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E8006: Check Fn::Or structure for validity.
/// Fn::Or must be an array of 2-10 elements.
pub struct E8006;

impl CfnLintRule for E8006 {
    fn id(&self) -> &str {
        "E8006"
    }

    fn short_description(&self) -> &str {
        "Check Fn::Or structure for validity"
    }

    fn description(&self) -> &str {
        "Check Fn::Or is a list of two to ten condition values"
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
        // Validation is handled by the engine's validate_condition_functions
        vec![]
    }
}

crate::register_cfn_lint_rule!(E8006);

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
    Fn::Or:
      - Fn::Equals:
          - a
          - b
Resources:
  B:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E8006.validate_template(&tmpl, &ast).is_empty());
    }
}
