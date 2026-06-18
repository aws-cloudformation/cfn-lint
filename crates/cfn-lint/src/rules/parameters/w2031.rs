use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// W2031: Check if parameters have a valid value based on AllowedPattern.
///
/// Schema-driven in Python — this is a no-op anchor in Rust.
pub struct W2031;

impl CfnLintRule for W2031 {
    fn id(&self) -> &str {
        "W2031"
    }

    fn short_description(&self) -> &str {
        "Check if parameters have a valid value based on an allowed pattern"
    }

    fn description(&self) -> &str {
        "Check if parameters have a valid value based on an allowed pattern"
    }

    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Schema-driven in Python — triggered by parent rule E3031
                vec![]
    }
}

crate::register_cfn_lint_rule!(W2031);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_noop() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
    Default: PROD123
    AllowedPattern: "[a-z]+"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2031.validate_template(&tmpl, &ast).is_empty());
    }
}
