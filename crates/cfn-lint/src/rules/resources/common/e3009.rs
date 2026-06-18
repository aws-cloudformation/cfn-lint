use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/other/resources/cfn_init.json"))
        .unwrap_or_default()
});

/// E3009: Check CloudFormation init configuration.
///
/// Mirrors Python cfn-lint `resources/CfnInit.py`. Validates that
/// `AWS::CloudFormation::Init` metadata has a valid structure.
pub struct E3009;

impl CfnLintRule for E3009 {
    fn id(&self) -> &str { "E3009" }
    fn short_description(&self) -> &str { "Check CloudFormation init configuration" }
    fn description(&self) -> &str {
        "Validate that the items in a CloudFormation init adhere to standards"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/Metadata/AWS::CloudFormation::Init"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let schema_validator = Validator::new(SCHEMA.clone());
        let errors = schema_validator.validate(instance, &SCHEMA, path);
        errors
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

crate::register_cfn_lint_rule!(E3009);
