use regex::Regex;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

pub struct E2003;

impl CfnLintRule for E2003 {
    fn id(&self) -> &str {
        "E2003"
    }

    fn short_description(&self) -> &str {
        "Parameters have appropriate names"
    }

    fn description(&self) -> &str {
        "Validates parameter names match allowed patterns"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        _root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let re = Regex::new(r"^[a-zA-Z0-9_-]+$").unwrap();
        template
            .parameters
            .keys()
            .filter(|name| !re.is_match(name))
            .map(|name| ValidationError {
                rule_id: Some(self.id().to_string()),
                message: format!(
                    "Parameter name '{}' must contain only alphanumeric characters, hyphens, and underscores",
                    name
                ),
                path: vec!["Parameters".to_string(), name.clone()],
                span: Default::default(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
})
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_parameter_names() {
        let yaml = br#"
Parameters:
  MyParam:
    Type: String
  my-param:
    Type: String
  my_param:
    Type: String
  Param123:
    Type: String
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E2003.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_invalid_parameter_name_with_space() {
        let yaml = br#"
Parameters:
  "My Param":
    Type: String
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E2003.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E2003"));
        assert!(issues[0].message.contains("My Param"));
    }

    #[test]
    fn test_no_parameters() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E2003.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E2003);
