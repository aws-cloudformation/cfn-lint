use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::template::Template;
use crate::transform::is_sam_template;

static TEMPLATE_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../data/schemas/other/template/template.json"
    ))
    .unwrap_or_default()
});

/// E1001: Basic CloudFormation Template Configuration.
///
/// Validates the root template against the template schema.
/// Catches missing 'Resources' section, invalid top-level keys, etc.
pub struct E1001;

impl CfnLintRule for E1001 {
    fn id(&self) -> &str {
        "E1001"
    }

    fn short_description(&self) -> &str {
        "Basic CloudFormation Template Configuration"
    }

    fn description(&self) -> &str {
        "Validates basic CloudFormation template structure via JSON Schema"
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
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let schema = &*TEMPLATE_SCHEMA;
        if schema.is_null() {
            return vec![];
        }

        let is_sam = is_sam_template(root);

        // Also check condition function arguments for null values.
        let mut issues: Vec<ValidationError> = Vec::new();
        for (name, node) in &template.conditions {
            check_condition_nulls(node, &["Conditions".to_string(), name.clone()], &mut issues);
        }

        let validator = Validator::new(schema.clone());
        issues.extend(
            validator
                .validate(root, schema, &vec![])
                .into_iter()
                .filter(|err| {
                    // Allow "Globals" section in SAM templates
                    !(is_sam && err.message.contains("\"Globals\""))
                })
                .map(|err| ValidationError {
                    rule_id: Some("E1001".to_string()),
                    message: err.message,
                    path: err.path,
                    span: err.span,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }),
        );

        issues
    }
}

/// Check for null values in condition function arguments.
fn check_condition_nulls(node: &AstNode, path: &[String], issues: &mut Vec<ValidationError>) {
    if node.is_null() {
        issues.push(ValidationError {
            rule_id: Some("E1001".to_string()),
            message:
                "None is not of type 'array', 'boolean', 'integer', 'number', 'object', 'string'"
                    .to_string(),
            path: path.to_vec(),
            span: node.span(),
            keyword: String::new(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        });
        return;
    }
    if let Some(func) = node.as_function() {
        check_condition_nulls(&func.args, path, issues);
    }
    if let Some(arr) = node.as_array() {
        for (i, elem) in arr.elements.iter().enumerate() {
            let mut child_path = path.to_vec();
            child_path.push(i.to_string());
            check_condition_nulls(elem, &child_path, issues);
        }
    }
    if let Some(obj) = node.as_object() {
        for (key, val) in obj.iter() {
            let mut child_path = path.to_vec();
            child_path.push(key.to_string());
            check_condition_nulls(val, &child_path, issues);
        }
    }
}

crate::register_cfn_lint_rule!(E1001);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_template() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\nResources:\n  MyBucket:\n    Type: AWS::S3::Bucket\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E1001.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_invalid_top_level_key() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\nResources:\n  MyBucket:\n    Type: AWS::S3::Bucket\nInvalidKey: foo\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1001.validate_template(&tmpl, &ast);
        assert!(!issues.is_empty());
        assert!(issues.iter().all(|i| i.rule_id.as_deref() == Some("E1001")));
    }

    #[test]
    fn test_condition_null_value() {
        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\nConditions:\n  MyCondition:\n    Fn::And:\n      -\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E1001.validate_template(&tmpl, &ast);
        assert!(issues
            .iter()
            .any(|i| i.rule_id.as_deref() == Some("E1001")
                && i.message.contains("None is not of type")));
    }
}
