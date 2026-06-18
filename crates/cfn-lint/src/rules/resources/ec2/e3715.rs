use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::json_schema_rule::validate_schema;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E3715;

impl CfnLintRule for E3715 {
    fn id(&self) -> &str { "E3715" }
    fn short_description(&self) -> &str { "VirtualName must use ephemeral device format when Ebs is absent" }
    fn description(&self) -> &str { "VirtualName must use ephemeral device format when Ebs is absent" }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*",
            "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*",
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*",
            "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/BlockDeviceMappings/*",
            "Resources/AWS::OpsWorks::Instance/Properties/BlockDeviceMappings/*",
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
        validate_schema("E3715", "VirtualName must use ephemeral device format when Ebs is absent", validator, instance, &SCHEMA, path)
    }
}

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::json!({
        "if": {
            "not": { "required": ["Ebs"] },
            "required": ["VirtualName"]
        },
        "then": {
            "properties": {
                "VirtualName": {
                    "pattern": "^ephemeral([0-9]|[1][0-9]|[2][0-3])$"
                }
            }
        }
    })
});

crate::register_cfn_lint_rule!(E3715);
