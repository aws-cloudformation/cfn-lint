use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::json_schema_rule::validate_schema;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3671: Validate block device mapping configuration.
///
/// Certain volume types require Iops to be specified. Applies to
/// `AWS::AutoScaling::LaunchConfiguration`, `AWS::EC2::Instance`,
/// `AWS::EC2::LaunchTemplate`, `AWS::EC2::SpotFleet`, and
/// `AWS::OpsWorks::Instance` block device mappings.
pub struct E3671;

impl CfnLintRule for E3671 {
    fn id(&self) -> &str {
        "E3671"
    }
    fn short_description(&self) -> &str {
        "Validate block device mapping configuration"
    }
    fn description(&self) -> &str {
        "Certain volume types require Iops to be specified"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/BlockDeviceMappings/*/Ebs",
            "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs",
            "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*/Ebs",
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*/Ebs",
            "Resources/AWS::OpsWorks::Instance/Properties/BlockDeviceMappings/*/Ebs",
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
            "E3671",
            "Validate block device mapping configuration",
            validator,
            instance,
            &SCHEMA,
            path,
        )
    }
}

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/extensions/aws_ec2_instance/blockdevicemappings.json"
    ))
    .unwrap_or_default()
});

crate::register_cfn_lint_rule!(E3671);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E3671.id(), "E3671");
        assert_eq!(E3671.severity(), Severity::Error);
        assert!(E3671.short_description().contains("block device"));
    }
}
