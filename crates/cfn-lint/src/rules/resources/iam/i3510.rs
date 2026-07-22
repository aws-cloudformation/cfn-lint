use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// I3510: Validate IAM statement resources match the actions.
///
/// Schema-driven in Python, needs proper IAM action-resource matching
pub struct I3510;

impl CfnLintRule for I3510 {
    fn id(&self) -> &str {
        "I3510"
    }

    fn short_description(&self) -> &str {
        "Validate statement resources match the actions"
    }

    fn description(&self) -> &str {
        "IAM policy statements have different constraints between actions and resources"
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
        // Schema-driven in Python, needs proper IAM action-resource matching
        vec![]
    }
}

crate::register_cfn_lint_rule!(I3510);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_stub_returns_empty() {
        let yaml = br#"
Resources:
  MyPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: test
      PolicyDocument:
        Statement:
          - Effect: Allow
            Action: s3:GetObject
            Resource: arn:aws:sqs:us-east-1:123456789012:my-queue
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I3510.validate_template(&tmpl, &ast).is_empty());
    }
}
