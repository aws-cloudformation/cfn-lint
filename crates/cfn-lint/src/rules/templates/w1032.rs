use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// W1032: Validate the values that come from a Fn::Join function.
/// Schema-driven anchor — resolved-value validation is handled by the schema validator.
pub struct W1032;

impl CfnLintRule for W1032 {
    fn id(&self) -> &str {
        "W1032"
    }

    fn short_description(&self) -> &str {
        "Validate resolved Fn::Join values"
    }

    fn description(&self) -> &str {
        "Resolve the Fn::Join and then validate the values against the schema"
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

crate::register_cfn_lint_rule!(W1032);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(W1032.id(), "W1032");
        assert_eq!(W1032.severity(), Severity::Warning);
    }

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName:
        Fn::Join:
          - "-"
          - - prefix
            - !Ref AWS::StackName
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1032.validate_template(&tmpl, &ast).is_empty());
    }
}
