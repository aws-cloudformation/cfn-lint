use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::template::Template;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../data/schemas/other/outputs/configuration.json"
    ))
    .unwrap_or_default()
});

/// E6001: Outputs have appropriate configuration.
pub struct E6001;

impl CfnLintRule for E6001 {
    fn id(&self) -> &str {
        "E6001"
    }
    fn short_description(&self) -> &str {
        "Outputs have appropriate configuration"
    }
    fn description(&self) -> &str {
        "Check if Outputs are properly configured"
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
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let outputs = match root.get("Outputs") {
            Some(n) => n,
            None => return vec![],
        };
        let validator = Validator::new(SCHEMA.clone());
        let base_path = vec!["Outputs".to_string()];
        validator
            .validate(outputs, &SCHEMA, &base_path)
            .into_iter()
            .filter(|e| !e.unknown)
            .map(|err| {
                let rule_id = match err.keyword.as_str() {
                    "maxProperties" => "E6010",
                    "propertyNames" | "maxLength" | "minLength" => "E6011",
                    "additionalProperties" => "E6004",
                    // Match Python cfn-lint's rule-id assignment: E6002 is
                    // "Outputs have required properties" (the `required`
                    // keyword) and E6003 is "Check the type of Outputs" (the
                    // `type` keyword). These were previously transposed.
                    "required" => "E6002",
                    "type" => "E6003",
                    _ => "E6001",
                };
                ValidationError {
                    rule_id: Some(rule_id.to_string()),
                    message: err.message,
                    path: err.path,
                    span: err.span,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }
            })
            .collect()
    }
}

crate::register_cfn_lint_rule!(E6001);
