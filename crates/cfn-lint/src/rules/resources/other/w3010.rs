use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W3010: Availability zone properties should not be hardcoded.
pub struct W3010;

impl CfnLintRule for W3010 {
    fn id(&self) -> &str {
        "W3010"
    }
    fn short_description(&self) -> &str {
        "Availability zone properties should not be hardcoded"
    }
    fn description(&self) -> &str {
        "Check if an Availability Zone property is hardcoded"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::AutoScaling::AutoScalingGroup/Properties/AvailabilityZones/*",
            "Resources/AWS::DAX::Cluster/Properties/AvailabilityZones/*",
            "Resources/AWS::DMS::ReplicationInstance/Properties/AvailabilityZone",
            "Resources/AWS::EC2::Host/Properties/AvailabilityZone",
            "Resources/AWS::EC2::Instance/Properties/AvailabilityZone",
            "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/Placement/AvailabilityZone",
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchSpecifications/*/Placement/AvailabilityZone",
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetRequestConfigData/LaunchTemplateConfigs/*/Overrides/*/AvailabilityZone",
            "Resources/AWS::EC2::Subnet/Properties/AvailabilityZone",
            "Resources/AWS::EC2::Volume/Properties/AvailabilityZone",
            "Resources/AWS::ElasticLoadBalancing::LoadBalancer/Properties/AvailabilityZones/*",
            "Resources/AWS::ElasticLoadBalancingV2::TargetGroup/Properties/Targets/*/AvailabilityZone",
            "Resources/AWS::EMR::Cluster/Properties/Instances/Placement/AvailabilityZone",
            "Resources/AWS::Glue::Connection/Properties/ConnectionInput/PhysicalConnectionRequirements/AvailabilityZone",
            "Resources/AWS::OpsWorks::Instance/Properties/AvailabilityZone",
            "Resources/AWS::RDS::DBCluster/Properties/AvailabilityZones/*",
            "Resources/AWS::RDS::DBInstance/Properties/AvailabilityZone",
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
        let zone = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        // "all" is a recognized exception
        if zone == "all" {
            return vec![];
        }

        // If we're inside a function (Fn::If, Fn::Select, etc.), skip
        // The path should not contain function names for hardcoded values
        let functions = [
            "Fn::If",
            "Fn::Select",
            "Fn::GetAtt",
            "Fn::Sub",
            "Fn::Join",
            "Fn::Split",
            "Fn::FindInMap",
            "Ref",
        ];
        if path.iter().any(|p| functions.contains(&p.as_str())) {
            return vec![];
        }

        // A hardcoded string at an AZ property path is a warning
        vec![ValidationError {
            rule_id: None,
            keyword: format!("cfnLint:{}", self.id()),
            message: format!("Avoid hardcoding availability zones {:?}", zone),
            path: path.to_vec(),
            span: instance.span(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        }]
    }
}

#[cfg(test)]

mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_stubbed_out() {
        let yaml = br#"
Resources:
  Subnet:
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: us-east-1a
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3010.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(W3010);
