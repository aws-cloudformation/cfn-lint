use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::json_schema_rule::validate_regional;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E3675;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/extensions/aws_emr_cluster/instancetypeconfig_instancetype_enum.json"))
        .unwrap_or_default()
});

impl CfnLintRule for E3675 {
    fn id(&self) -> &str {
        "E3675"
    }
    fn short_description(&self) -> &str {
        "Validate EMR cluster instance type"
    }
    fn description(&self) -> &str {
        "Validate EMR cluster instance type"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::EMR::Cluster/Properties/Instances/CoreInstanceFleet/InstanceTypeConfigs/*/InstanceType",
            "Resources/AWS::EMR::Cluster/Properties/Instances/CoreInstanceGroup/InstanceType",
            "Resources/AWS::EMR::Cluster/Properties/Instances/TaskInstanceFleets/*/InstanceTypeConfigs/*/InstanceType",
            "Resources/AWS::EMR::Cluster/Properties/Instances/TaskInstanceGroups/*/InstanceType",
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
        validate_regional(
            self.id(),
            self.short_description(),
            validator,
            instance,
            &SCHEMA,
            path,
        )
    }
}

crate::register_cfn_lint_rule!(E3675);
