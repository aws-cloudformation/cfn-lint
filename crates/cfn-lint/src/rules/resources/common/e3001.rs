use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/other/resources/configuration.json"))
        .unwrap_or_default()
});

/// E3001: Basic CloudFormation Resource Check.
///
/// Validates the Resources section against its configuration schema:
/// - Resource names match pattern ^[a-zA-Z0-9]+$
/// - Max 500 resources
/// - Each resource has valid top-level keys (Type, Properties, Condition, etc.)
pub struct E3001;

impl CfnLintRule for E3001 {
    fn id(&self) -> &str { "E3001" }
    fn short_description(&self) -> &str { "Validate basic resource configuration" }
    fn description(&self) -> &str {
        "Validates basic CloudFormation resource configuration"
    }
    fn severity(&self) -> Severity { Severity::Error }
    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let resources = match root.get("Resources") {
            Some(r) => r,
            None => return vec![],
        };

        let validator = Validator::new_strict(SCHEMA.clone());
        let base_path = vec!["Resources".to_string()];

        validator
            .validate(resources, &SCHEMA, &base_path)
            .into_iter()
            .filter(|e| !e.unknown)
            .map(|err| {
                let rule_id = match err.keyword.as_str() {
                    "maxProperties" => "E3010",
                    "propertyNames" | "maxLength" | "minLength" => "E3011",
                    "patternProperties" | "additionalProperties" => "E3001",
                    _ => "E3001",
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

crate::register_cfn_lint_rule!(E3001);
