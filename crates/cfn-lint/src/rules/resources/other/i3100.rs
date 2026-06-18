use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use regex::Regex;

/// I3100: Checks for legacy instance type generations.
///
/// New instance type generations increase performance and decrease cost.
pub struct I3100;

impl CfnLintRule for I3100 {
    fn id(&self) -> &str {
        "I3100"
    }
    fn short_description(&self) -> &str {
        "Checks for legacy instance type generations"
    }
    fn description(&self) -> &str {
        "New instance type generations increase performance and decrease cost"
    }
    fn severity(&self) -> Severity {
        Severity::Informational
    }

    fn keywords(&self) -> &[&str] {
        &[
            // Direct instance type properties
            "Resources/AWS::AutoScaling::LaunchConfiguration/Properties/InstanceType",
            "Resources/AWS::EC2::CapacityReservation/Properties/InstanceType",
            "Resources/AWS::EC2::Host/Properties/InstanceType",
            "Resources/AWS::EC2::Instance/Properties/InstanceType",
            "Resources/AWS::RDS::DBInstance/Properties/DBInstanceClass",
            "Resources/AWS::ElastiCache::CacheCluster/Properties/CacheNodeType",
            "Resources/AWS::ElastiCache::GlobalReplicationGroup/Properties/CacheNodeType",
            "Resources/AWS::ElastiCache::ReplicationGroup/Properties/CacheNodeType",
            // Nested instance type properties
            "Resources/AWS::EC2::EC2Fleet/Properties/FleetLaunchTemplateOverridesRequest/InstanceType",
            "Resources/AWS::EC2::LaunchTemplate/Properties/LaunchTemplateData/InstanceType",
            "Resources/AWS::EC2::SpotFleet/Properties/SpotFleetLaunchSpecification/InstanceType",
            "Resources/AWS::OpenSearchService::Domain/Properties/ClusterConfig/InstanceType",
            "Resources/AWS::Elasticsearch::Domain/Properties/ElasticsearchClusterConfig/InstanceType",
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
        let val = match instance.as_str() {
            Some(v) => v,
            None => return vec![],
        };

        if is_previous_gen(val) {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!("Upgrade previous generation instance type: {}", val),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

fn is_previous_gen(instance_type: &str) -> bool {
    let re = Regex::new(r"(^|\.)([cmr][1-3]|cc2|cg1|cr1|g2|hi1|hs1|i2|t1)($|\.)").unwrap();
    re.is_match(instance_type)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_current_gen_no_issue() {
        let yaml = br#"
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: m5.large
      ImageId: ami-12345678
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Instance")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("InstanceType")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Instance".to_string(),
            "Properties".to_string(),
            "InstanceType".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I3100.validate(
            &validator,
            "Resources/AWS::EC2::Instance/Properties/InstanceType",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_previous_gen_flagged() {
        let yaml = br#"
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: m1.large
      ImageId: ami-12345678
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Instance")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("InstanceType")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Instance".to_string(),
            "Properties".to_string(),
            "InstanceType".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I3100.validate(
            &validator,
            "Resources/AWS::EC2::Instance/Properties/InstanceType",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("m1.large"));
    }
}

crate::register_cfn_lint_rule!(I3100);
