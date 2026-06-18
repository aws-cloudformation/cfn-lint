use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E2900: Validate deployment file parameters against template parameters.
///
/// Validates that required properties are provided, allowed values are valid,
/// types are correct, and patterns match in a deployment file for the
/// parameters specified in a template.
pub struct E2900;

impl CfnLintRule for E2900 {
    fn id(&self) -> &str {
        "E2900"
    }

    fn short_description(&self) -> &str {
        "Validate deployment file parameters"
    }

    fn description(&self) -> &str {
        "Validate deployment file parameters"
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
        // Deployment file parameter validation is handled at the runner level
        // when deployment files are provided. This rule serves as a registry anchor.
        vec![]
    }
}

crate::register_cfn_lint_rule!(E2900);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E2900.id(), "E2900");
        assert_eq!(E2900.severity(), Severity::Error);
    }

    #[test]
    fn test_returns_empty() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
    AllowedValues:
      - dev
      - prod
"#;
        let ast = crate::parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E2900.validate_template(&tmpl, &ast).is_empty());
    }
}
