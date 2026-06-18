use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// W1040: Validate the values that come from a Fn::ToJsonString function.
/// Schema-driven anchor — resolved-value validation is handled by the schema validator.
pub struct W1040;

impl CfnLintRule for W1040 {
    fn id(&self) -> &str {
        "W1040"
    }

    fn short_description(&self) -> &str {
        "Validate resolved Fn::ToJsonString values"
    }

    fn description(&self) -> &str {
        "Resolve the Fn::ToJsonString and then validate the values against the schema"
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

crate::register_cfn_lint_rule!(W1040);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(W1040.id(), "W1040");
        assert_eq!(W1040.severity(), Severity::Warning);
    }

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: my-func
      Runtime: python3.9
      Handler: index.handler
      Code:
        ZipFile: |
          def handler(event, context):
            pass
      Environment:
        Variables:
          CONFIG:
            Fn::ToJsonString:
              key: value
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1040.validate_template(&tmpl, &ast).is_empty());
    }
}
