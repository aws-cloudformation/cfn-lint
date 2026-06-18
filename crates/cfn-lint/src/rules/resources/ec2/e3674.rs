use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::json_schema_rule::validate_schema;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E3674;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/extensions/aws_ec2_instance/privateipaddress.json"
    ))
    .unwrap_or_default()
});

impl CfnLintRule for E3674 {
    fn id(&self) -> &str {
        "E3674"
    }
    fn short_description(&self) -> &str {
        "Primary cannot be True when PrivateIpAddress is specified"
    }
    fn description(&self) -> &str {
        "Primary cannot be True when PrivateIpAddress is specified"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::EC2::Instance/Properties",
            "Resources/AWS::EC2::NetworkInterface/Properties",
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
        validate_schema(
            self.id(),
            self.short_description(),
            validator,
            instance,
            &SCHEMA,
            path,
        )
    }
}

crate::register_cfn_lint_rule!(E3674);
