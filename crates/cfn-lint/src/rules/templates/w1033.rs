use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// W1033: Validate the values that come from a Fn::Split function.
/// Schema-driven anchor — resolved-value validation is handled by the schema validator.
pub struct W1033;

impl CfnLintRule for W1033 {
    fn id(&self) -> &str {
        "W1033"
    }

    fn short_description(&self) -> &str {
        "Validate resolved Fn::Split values"
    }

    fn description(&self) -> &str {
        "Resolve the Fn::Split and then validate the values against the schema"
    }

    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(W1033);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(W1033.id(), "W1033");
        assert_eq!(W1033.severity(), Severity::Warning);
    }

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      Tags:
        - Key: Name
          Value:
            Fn::Select:
              - 0
              - Fn::Split:
                  - ","
                  - "a,b,c"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1033.validate_template(&tmpl, &ast).is_empty());
    }
}
