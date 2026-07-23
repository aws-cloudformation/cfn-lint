use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// Template body size limit in bytes (1 MB).
const TEMPLATE_BODY_LIMIT: usize = 1_000_000;
/// Threshold fraction at which to warn.
const THRESHOLD: f64 = 0.9;

/// I1002: Validate that the template size is approaching the upper limit.
pub struct I1002;

impl I1002 {
    /// Validate with an explicit byte size (for testability and when the caller
    /// already knows the file size).
    pub fn validate_size(
        &self,
        byte_size: usize,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let limit = (TEMPLATE_BODY_LIMIT as f64 * THRESHOLD) as usize;
        if byte_size > limit && byte_size <= TEMPLATE_BODY_LIMIT {
            vec![ValidationError {
                rule_id: Some(self.id().to_string()),
                message: format!(
                    "The template file size ({} bytes) is approaching the limit ({} bytes)",
                    byte_size, TEMPLATE_BODY_LIMIT
                ),
                path: vec!["Template".to_string()],
                span: root.span(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }]
        } else {
            vec![]
        }
    }
}

impl CfnLintRule for I1002 {
    fn id(&self) -> &str {
        "I1002"
    }
    fn short_description(&self) -> &str {
        "Validate approaching the template size limit"
    }
    fn description(&self) -> &str {
        "Check the size of the template is approaching the upper limit"
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
        // File-size check requires the raw byte length, which is passed via
        // validate_size() from the runner. The trait method alone cannot access
        // the original file bytes, so it returns nothing.
        vec![]
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_small_template_no_issue() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\n";
        let ast = parser::parse(yaml).unwrap();
        assert!(I1002.validate_size(yaml.len(), &ast).is_empty());
    }

    #[test]
    fn test_approaching_limit_warns() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\n";
        let ast = parser::parse(yaml).unwrap();
        // 950_000 bytes is above 90% of 1_000_000 but under the limit
        let issues = I1002.validate_size(950_000, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("I1002"));
        assert_eq!(issues[0].rule_id.as_deref(), Some("I1002"));
        assert!(issues[0].message.contains("950000"));
        assert!(issues[0].message.contains("1000000"));
    }
}

crate::register_cfn_lint_rule!(I1002);
