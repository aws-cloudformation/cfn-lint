use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static TRANSFORM_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../data/schemas/other/transforms/configuration.json"
    ))
    .unwrap_or_default()
});

/// E1005: Validate Transform configuration.
///
/// Validates the Transform section of the template against the transforms
/// configuration schema. Catches invalid transform names and configurations.
pub struct E1005;

impl CfnLintRule for E1005 {
    fn id(&self) -> &str {
        "E1005"
    }

    fn short_description(&self) -> &str {
        "Validate Transform configuration"
    }

    fn description(&self) -> &str {
        "Validates the Transform section of the template is properly configured"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let transform = match root.get("Transform") {
            Some(t) => t,
            None => return vec![],
        };

        // Skip if it's a function (e.g. !Sub)
        if transform.as_function().is_some() {
            return vec![];
        }

        let schema = &*TRANSFORM_SCHEMA;
        if schema.is_null() {
            return vec![];
        }

        let validator = Validator::new(schema.clone());
        let base_path = vec!["Transform".to_string()];
        validator
            .validate(transform, schema, &base_path)
            .into_iter()
            .map(|err| ValidationError {
                rule_id: Some("E1005".to_string()),
                message: err.message,
                path: err.path,
                span: err.span,
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
            schema_id: None,
            })
            .collect()
    }
}

crate::register_cfn_lint_rule!(E1005);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_no_transform() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\nResources:\n  MyBucket:\n    Type: AWS::S3::Bucket\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E1005.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_valid_transform() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\nTransform: AWS::Serverless-2016-10-31\nResources:\n  MyBucket:\n    Type: AWS::S3::Bucket\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E1005.validate_template(&tmpl, &ast).is_empty());
    }
}
