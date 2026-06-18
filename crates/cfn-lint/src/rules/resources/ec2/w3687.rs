use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::json_schema_rule::validate_schema;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W3687;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/extensions/aws_ec2_securitygroup/protocols_and_port_ranges_exclude.json"))
        .unwrap_or_default()
});

impl CfnLintRule for W3687 {
    fn id(&self) -> &str {
        "W3687"
    }
    fn short_description(&self) -> &str {
        "Validate that ports are not specified for certain protocols"
    }
    fn description(&self) -> &str {
        "Validate that ports are not specified for certain protocols"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::EC2::SecurityGroup/Properties/SecurityGroupIngress/*",
            "Resources/AWS::EC2::SecurityGroup/Properties/SecurityGroupEgress/*",
            "Resources/AWS::EC2::SecurityGroupEgress/Properties",
            "Resources/AWS::EC2::SecurityGroupIngress/Properties",
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

crate::register_cfn_lint_rule!(W3687);
