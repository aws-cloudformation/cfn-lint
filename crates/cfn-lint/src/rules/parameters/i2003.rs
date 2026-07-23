use regex::Regex;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// I2003: Validate AllowedPattern is a valid regex.
///
/// Validate the pattern defined in AllowedPattern. This is informational
/// as the service side regex library may differ.
pub struct I2003;

impl CfnLintRule for I2003 {
    fn id(&self) -> &str {
        "I2003"
    }
    fn short_description(&self) -> &str {
        "Validate AllowedPattern is a valid regex"
    }
    fn description(&self) -> &str {
        "Validate the pattern defined in AllowedPattern. This is informational \
         as the service side regex library is different than the Rust one"
    }
    fn severity(&self) -> Severity {
        Severity::Informational
    }

    fn keywords(&self) -> &[&str] {
        &["Parameters/*/AllowedPattern"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let pattern = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        if Regex::new(pattern).is_err() {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!("{:?} could not be compiled as a valid regex", pattern),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_valid_pattern() {
        let yaml = br#"
Parameters:
  Name:
    Type: String
    AllowedPattern: "^[a-zA-Z0-9]+$"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I2003.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_invalid_pattern_stub() {
        let yaml = br#"
Parameters:
  Name:
    Type: String
    AllowedPattern: "[invalid("
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(I2003.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(I2003);
