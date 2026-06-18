use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../data/schemas/other/metadata/configuration.json"))
        .unwrap_or_default()
});

/// E4002: Validate the configuration of the Metadata section.
pub struct E4002;

impl CfnLintRule for E4002 {
    fn id(&self) -> &str { "E4002" }
    fn short_description(&self) -> &str { "Validate Metadata section configuration" }
    fn description(&self) -> &str {
        "Validates that Metadata section is an object and has no null values"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["Metadata"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let schema_validator = crate::jsonschema::Validator::new(SCHEMA.clone());
        schema_validator
            .validate(instance, &SCHEMA, path)
            .into_iter()
            .map(|mut err| {
                if err.keyword.is_empty() {
                    err.keyword = format!("cfnLint:{}", self.id());
                }
                err
            })
            .collect()
    }
}

crate::register_cfn_lint_rule!(E4002);
