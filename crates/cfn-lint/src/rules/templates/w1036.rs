use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// W1036: Validate the values that come from a Fn::GetAZs function.
/// Schema-driven anchor — resolved-value validation is handled by the schema validator.
pub struct W1036;

impl CfnLintRule for W1036 {
    fn id(&self) -> &str {
        "W1036"
    }

    fn short_description(&self) -> &str {
        "Validate resolved Fn::GetAZs values"
    }

    fn description(&self) -> &str {
        "Resolve the Fn::GetAZs and then validate the values against the schema"
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

crate::register_cfn_lint_rule!(W1036);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_metadata() {
        assert_eq!(W1036.id(), "W1036");
        assert_eq!(W1036.severity(), Severity::Warning);
    }

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Resources:
  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: vpc-123
      CidrBlock: 10.0.0.0/24
      AvailabilityZone:
        Fn::Select:
          - 0
          - Fn::GetAZs: !Ref "AWS::Region"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W1036.validate_template(&tmpl, &ast).is_empty());
    }
}
