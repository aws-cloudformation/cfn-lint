use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/resources/metadata.json"
    ))
    .unwrap_or_default()
});

/// E3028: Validate the metadata section of a resource.
pub struct E3028;

impl CfnLintRule for E3028 {
    fn id(&self) -> &str {
        "E3028"
    }
    fn short_description(&self) -> &str {
        "Validate the metadata section of a resource"
    }
    fn description(&self) -> &str {
        "The metadata section must be an object if present"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/Metadata"]
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

crate::register_cfn_lint_rule!(E3028);
