use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E8003: Check Fn::Equals structure for validity.
/// Fn::Equals must be an array of exactly 2 elements.
pub struct E8003;

impl CfnLintRule for E8003 {
    fn id(&self) -> &str {
        "E8003"
    }

    fn short_description(&self) -> &str {
        "Check Fn::Equals structure for validity"
    }

    fn description(&self) -> &str {
        "Check Fn::Equals is a list of two elements"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Validation is handled by the schema pipeline's fn_equals keyword (maps to "E8003")
                vec![]
    }
}

crate::register_cfn_lint_rule!(E8003);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_validate_is_stub() {
        // Validation is handled by the schema pipeline's fn_equals keyword;
        // this rule struct is only a metadata holder for the rule registry.
        let yaml = br#"
Conditions:
  Bad:
    Fn::Equals:
      - a
      - b
      - c
Resources:
  B:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E8003.validate_template(&tmpl, &ast).is_empty());
    }
}
