use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// I3013: Check resources with auto-expiring content have explicit retention period.
pub struct I3013;

const RETENTION_CHECKS: &[(&str, &[&str])] = &[
    ("AWS::Kinesis::Stream", &["RetentionPeriodHours"]),
    ("AWS::SQS::Queue", &["MessageRetentionPeriod"]),
    ("AWS::DocDB::DBCluster", &["BackupRetentionPeriod"]),
    (
        "AWS::Synthetics::Canary",
        &["SuccessRetentionPeriod", "FailureRetentionPeriod"],
    ),
    (
        "AWS::Redshift::Cluster",
        &["AutomatedSnapshotRetentionPeriod"],
    ),
    ("AWS::RDS::DBCluster", &["BackupRetentionPeriod"]),
];

impl I3013 {
    /// Python uses an if/then schema: require BackupRetentionPeriod only when
    /// Engine is present, doesn't start with "aurora", and SourceDBInstanceIdentifier is absent.
    fn rds_dbinstance_needs_retention(props: &crate::ast::ObjectNode) -> bool {
        // SourceDBInstanceIdentifier must not be present
        if props.get("SourceDBInstanceIdentifier").is_some() {
            return false;
        }
        // Engine must be present and not start with "aurora"
        match props.get("Engine").and_then(|n| n.as_str()) {
            Some(engine) => !engine.starts_with("aurora"),
            None => false,
        }
    }
}

impl CfnLintRule for I3013 {
    fn id(&self) -> &str {
        "I3013"
    }
    fn short_description(&self) -> &str {
        "Check resources with auto expiring content have explicit retention period"
    }
    fn description(&self) -> &str {
        "The default retention period will delete the data after a pre-defined time. \
         Set explicit values to avoid data loss on resource"
    }
    fn severity(&self) -> Severity {
        Severity::Informational
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::RDS::DBInstance/Properties",
            "Resources/AWS::Kinesis::Stream/Properties",
            "Resources/AWS::SQS::Queue/Properties",
            "Resources/AWS::DocDB::DBCluster/Properties",
            "Resources/AWS::Synthetics::Canary/Properties",
            "Resources/AWS::Redshift::Cluster/Properties",
            "Resources/AWS::RDS::DBCluster/Properties",
        ]
    }

    fn validate(
        &self,
        _validator: &Validator,
        keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let props = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        // Determine resource type from the keyword path
        // keyword is like "Resources/AWS::RDS::DBInstance/Properties"
        let resource_type = keyword
            .strip_prefix("Resources/")
            .and_then(|s| s.strip_suffix("/Properties"))
            .unwrap_or("");

        // AWS::RDS::DBInstance has conditional logic
        if resource_type == "AWS::RDS::DBInstance" {
            if !Self::rds_dbinstance_needs_retention(props) {
                return vec![];
            }
            if props.get("BackupRetentionPeriod").is_none() {
                return vec![ValidationError {
                    rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: format!(
                        "'BackupRetentionPeriod' is missing (The default retention period will \
                         delete the data after a pre-defined time. Set an explicit value to \
                         avoid data loss on resource)"
                    ),
                    path: path.to_vec(),
                    span: instance.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }];
            }
            return vec![];
        }

        // For other resource types, check the required attributes
        let required_attrs = match RETENTION_CHECKS.iter().find(|(t, _)| *t == resource_type) {
            Some((_, attrs)) => attrs,
            None => return vec![],
        };

        let mut errors = Vec::new();
        for attr in *required_attrs {
            if props.get(attr).is_none() {
                errors.push(ValidationError {
                    rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: format!(
                        "'{}' is missing (The default retention period will \
                         delete the data after a pre-defined time. Set an explicit value to \
                         avoid data loss on resource)",
                        attr
                    ),
                    path: path.to_vec(),
                    span: instance.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
            }
        }

        errors
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_rds_with_retention_ok() {
        let yaml = br#"
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: mysql
      BackupRetentionPeriod: 7
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("DB")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "DB".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I3013.validate(
            &validator,
            "Resources/AWS::RDS::DBInstance/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_rds_missing_retention_non_aurora() {
        let yaml = br#"
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: mysql
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("DB")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "DB".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I3013.validate(
            &validator,
            "Resources/AWS::RDS::DBInstance/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("BackupRetentionPeriod"));
    }

    #[test]
    fn test_rds_aurora_engine_skipped() {
        let yaml = br#"
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.r5.large
      Engine: aurora-postgresql
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("DB")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "DB".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I3013.validate(
            &validator,
            "Resources/AWS::RDS::DBInstance/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_rds_source_db_skipped() {
        let yaml = br#"
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: mysql
      SourceDBInstanceIdentifier: source-db
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("DB")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "DB".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I3013.validate(
            &validator,
            "Resources/AWS::RDS::DBInstance/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }
}

crate::register_cfn_lint_rule!(I3013);
