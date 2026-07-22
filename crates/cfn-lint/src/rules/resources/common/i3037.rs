use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// I3037: Check if a list that allows duplicates has any duplicates.
///
/// Schema-driven in Python via uniqueItems keyword
pub struct I3037;

impl CfnLintRule for I3037 {
    fn id(&self) -> &str {
        "I3037"
    }

    fn short_description(&self) -> &str {
        "Check if a list that allows duplicates has any duplicates"
    }

    fn description(&self) -> &str {
        "Check if a list that allows duplicates has any duplicates"
    }

    fn severity(&self) -> Severity {
        Severity::Informational
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        _root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        // Schema-driven in Python via uniqueItems keyword
        vec![]
    }
}

crate::register_cfn_lint_rule!(I3037);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.12
      Handler: index.handler
      Code:
        ZipFile: "x"
      Layers:
        - arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1
        - arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I3037.validate_template(&tmpl, &ast).is_empty());
    }
}
