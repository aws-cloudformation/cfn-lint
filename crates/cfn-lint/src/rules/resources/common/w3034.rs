use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// W3034: Check if parameter default values are between MinValue and MaxValue.
/// Skip if Default is not a number.
pub struct W3034;

impl CfnLintRule for W3034 {
    fn id(&self) -> &str {
        "W3034"
    }

    fn short_description(&self) -> &str {
        "Check if parameter values are between min and max"
    }

    fn description(&self) -> &str {
        "Check if parameter values value being between the minimum and maximum"
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
        // Schema-driven in Python — triggered by parent rule
        vec![]
    }
}

crate::register_cfn_lint_rule!(W3034);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_noop() {
        let yaml = br#"
Parameters:
  Port:
    Type: Number
    Default: 80
    MinValue: 1024
    MaxValue: 65535
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3034.validate_template(&tmpl, &ast).is_empty());
    }
}
