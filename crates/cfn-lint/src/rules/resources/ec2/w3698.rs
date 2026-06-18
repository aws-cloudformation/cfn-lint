use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::json_schema_rule::validate_schema;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W3698;

impl CfnLintRule for W3698 {
    fn id(&self) -> &str {
        "W3698"
    }
    fn short_description(&self) -> &str {
        "VirtualName is ignored when Ebs is specified"
    }
    fn description(&self) -> &str {
        "VirtualName is ignored when Ebs is specified"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

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
        validate_schema(
            "W3698",
            "VirtualName is ignored when Ebs is specified",
            validator,
            instance,
            &SCHEMA,
            path,
        )
    }
}

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::json!({
        "not": {
            "required": ["VirtualName", "Ebs"]
        }
    })
});

crate::register_cfn_lint_rule!(W3698);
