use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../data/schemas/other/mappings/configuration.json"))
        .unwrap_or_default()
});

/// E7001: Mappings have appropriate configuration.
pub struct E7001;

impl CfnLintRule for E7001 {
    fn id(&self) -> &str {
        "E7001"
    }
    fn short_description(&self) -> &str {
        "Mappings have appropriate configuration"
    }
    fn description(&self) -> &str {
        "Check if Mappings are properly configured"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }
    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let mappings = match root.get("Mappings") {
            Some(n) => n,
            None => return vec![],
        };
        let validator = Validator::new(SCHEMA.clone());
        let base_path = vec!["Mappings".to_string()];
        validator
            .validate(mappings, &SCHEMA, &base_path)
            .into_iter()
            .filter(|e| !e.unknown)
            .map(|err| {
                let rule_id = match err.keyword.as_str() {
                    "maxProperties" | "minProperties" => "E7010",
                    "propertyNames" | "maxLength" | "minLength" => "E7002",
                    "type" => "E7001",
                    "patternProperties" | "additionalProperties" => "E7001",
                    _ => "E7001",
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

crate::register_cfn_lint_rule!(E7001);
