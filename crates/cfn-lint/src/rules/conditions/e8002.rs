use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E8002: Check if the referenced Conditions are defined.
///
/// In Python, this rule provides a `cfncondition` validator keyword that is
/// triggered by the schema engine. Since no schema currently uses this keyword,
/// this rule is effectively a no-op anchor.
pub struct E8002;

impl CfnLintRule for E8002 {
    fn id(&self) -> &str {
        "E8002"
    }

    fn short_description(&self) -> &str {
        "Check if the referenced Conditions are defined"
    }

    fn description(&self) -> &str {
        "Making sure the used conditions are actually defined in the Conditions section"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // In Python, this is a cfncondition validator keyword triggered by the schema engine.
                // No schema currently uses this keyword, so this is a no-op.
                vec![]
    }
}

crate::register_cfn_lint_rule!(E8002);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_noop() {
        let yaml = br#"
Conditions:
  IsProd:
    Fn::Equals:
      - !Ref AWS::Region
      - us-east-1
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Condition: IsProd
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E8002.validate_template(&tmpl, &ast).is_empty());
    }
}
