use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::jsonschema::Validator;
use crate::rules::Severity;

const NO_IOPS_VOLUME_TYPES: &[&str] = &["gp2", "st1", "sc1", "standard"];

/// W3671: Iops is ignored for certain EBS volume types.
///
/// When Iops is specified with volume types gp2, st1, sc1, or standard,
/// the value is silently ignored. Remove Iops or use a volume type
/// that supports provisioned IOPS (io1, io2, gp3).
pub struct W3671;

impl CfnLintRule for W3671 {
    fn id(&self) -> &str { "W3671" }
    fn short_description(&self) -> &str { "Iops is ignored for certain EBS volume types" }
    fn severity(&self) -> Severity { Severity::Warning }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::EC2::Instance/Properties/BlockDeviceMappings/*/Ebs",
            "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/BlockDeviceMappings/*/Ebs",
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/BlockDeviceMappings/*/Ebs",
            "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/BlockDeviceMappings/*/Ebs",
            "Resources/AWS::OpsWorks::Instance/Properties/BlockDeviceMappings/*/Ebs",
        ]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let obj = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        let volume_type = match obj.get("VolumeType").and_then(|v| v.as_str()) {
            Some(vt) => vt,
            None => return vec![],
        };

        if NO_IOPS_VOLUME_TYPES.contains(&volume_type) && obj.get("Iops").is_some() {
            let mut iops_path = path.to_vec();
            iops_path.push("Iops".to_string());
            vec![ValidationError {
                rule_id: Some(self.id().to_string()),
                keyword: format!("cfnLint:{}", self.id()),
                message: format!("'Iops' is ignored when 'VolumeType' is '{}'", volume_type),
                path: iops_path,
                span: obj.get("Iops").map(|n| n.span()).unwrap_or_default(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }]
        } else {
            vec![]
        }
    }
}

crate::register_cfn_lint_rule!(W3671);
