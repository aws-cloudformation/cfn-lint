use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// W1031: Validate the values that come from a Fn::Sub function.
/// Schema-driven anchor — resolved-value validation is handled by the schema validator.
pub struct W1031;

impl CfnLintRule for W1031 {
    fn id(&self) -> &str {
        "W1031"
    }

    fn short_description(&self) -> &str {
        "Validate resolved Fn::Sub values"
    }

    fn description(&self) -> &str {
        "Resolve the Fn::Sub and then validate the values against the schema"
    }

    fn severity(&self) -> Severity {
        Severity::Warning
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

crate::register_cfn_lint_rule!(W1031);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(W1031.id(), "W1031");
        assert_eq!(W1031.severity(), Severity::Warning);
    }

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub "my-${AWS::Region}-bucket"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1031.validate_template(&tmpl, &ast).is_empty());
    }
}
