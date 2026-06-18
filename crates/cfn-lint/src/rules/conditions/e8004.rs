use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E8004: Check Fn::And structure for validity.
/// Fn::And must be an array of 2-10 elements.
pub struct E8004;

impl CfnLintRule for E8004 {
    fn id(&self) -> &str {
        "E8004"
    }

    fn short_description(&self) -> &str {
        "Check Fn::And structure for validity"
    }

    fn description(&self) -> &str {
        "Check Fn::And is a list of two to ten condition values"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        _root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        // Validation is handled by the schema pipeline's fn_condition keyword (maps to "E8004")
        vec![]
    }
}

crate::register_cfn_lint_rule!(E8004);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_validate_is_stub() {
        // Validation is handled by the schema pipeline's fn_condition keyword;
        // this rule struct is only a metadata holder for the rule registry.
        let yaml = br#"
Conditions:
  Bad:
    Fn::And:
      - Fn::Equals:
          - a
          - b
Resources:
  B:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E8004.validate_template(&tmpl, &ast).is_empty());
    }
}
