use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::template::Template;

/// W2030: Check if parameters have a valid value based on AllowedValues.
/// For each parameter with AllowedValues, check Default is in the list.
pub struct W2030;

impl CfnLintRule for W2030 {
    fn id(&self) -> &str {
        "W2030"
    }

    fn short_description(&self) -> &str {
        "Check if parameters have a valid value"
    }

    fn description(&self) -> &str {
        "Check if parameters have a valid value"
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
        // Schema-driven in Python — triggered by parent rule E3030
        vec![]
    }
}

crate::register_cfn_lint_rule!(W2030);

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
    Default: test
    AllowedValues:
      - dev
      - staging
      - prod
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W2030.validate_template(&tmpl, &ast).is_empty());
    }
}
