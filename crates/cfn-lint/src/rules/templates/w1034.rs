use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// W1034: Validate the values that come from a Fn::FindInMap function.
/// Schema-driven anchor — resolved-value validation is handled by the schema validator.
pub struct W1034;

impl CfnLintRule for W1034 {
    fn id(&self) -> &str {
        "W1034"
    }

    fn short_description(&self) -> &str {
        "Validate resolved Fn::FindInMap values"
    }

    fn description(&self) -> &str {
        "Resolve the Fn::FindInMap and then validate the values against the schema"
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

crate::register_cfn_lint_rule!(W1034);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(W1034.id(), "W1034");
        assert_eq!(W1034.severity(), Severity::Warning);
    }

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Mappings:
  RegionMap:
    us-east-1:
      AMI: ami-12345
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !FindInMap [RegionMap, us-east-1, AMI]
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1034.validate_template(&tmpl, &ast).is_empty());
    }
}
