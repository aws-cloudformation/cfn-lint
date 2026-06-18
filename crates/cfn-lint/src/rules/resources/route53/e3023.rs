use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::json_schema_rule::validate_schema;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/extensions/aws_route53_recordset/recordset_pattern.json"))
        .unwrap_or_default()
});

pub struct E3023;

impl CfnLintRule for E3023 {
    fn id(&self) -> &str { "E3023" }
    fn short_description(&self) -> &str { "Validate Route53 RecordSets" }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::Route53::RecordSet/Properties",
            "Resources/AWS::Route53::RecordSetGroup/Properties/RecordSets/*",
        ]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        validate_schema("E3023", "Validate Route53 RecordSets", validator, instance, &SCHEMA, path)
    }
}

crate::register_cfn_lint_rule!(E3023);
