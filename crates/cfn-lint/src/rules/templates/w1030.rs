use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// W1030: Validate the values that come from a Ref function.
/// Schema-driven anchor — resolved-value validation is handled by the schema validator.
pub struct W1030;

impl CfnLintRule for W1030 {
    fn id(&self) -> &str {
        "W1030"
    }

    fn short_description(&self) -> &str {
        "Validate resolved Ref values"
    }

    fn description(&self) -> &str {
        "Resolve the Ref and then validate the values against the schema"
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

crate::register_cfn_lint_rule!(W1030);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(W1030.id(), "W1030");
        assert_eq!(W1030.severity(), Severity::Warning);
    }

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref Env
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1030.validate_template(&tmpl, &ast).is_empty());
    }
}
