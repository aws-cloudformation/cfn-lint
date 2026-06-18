use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../data/schemas/other/metadata/interface.json"
    ))
    .unwrap_or_default()
});

/// E4001: Metadata Interface have appropriate properties.
pub struct E4001;

impl CfnLintRule for E4001 {
    fn id(&self) -> &str {
        "E4001"
    }
    fn short_description(&self) -> &str {
        "Metadata Interface have appropriate properties"
    }
    fn description(&self) -> &str {
        "Metadata Interface properties are properly configured"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Metadata/AWS::CloudFormation::Interface"]
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

crate::register_cfn_lint_rule!(E4001);
