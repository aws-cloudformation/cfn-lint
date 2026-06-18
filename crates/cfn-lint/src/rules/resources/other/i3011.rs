use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// I3011: Stateful resources should have DeletionPolicy and UpdateReplacePolicy.
pub struct I3011;

impl CfnLintRule for I3011 {
    fn id(&self) -> &str {
        "I3011"
    }
    fn short_description(&self) -> &str {
        "Check stateful resources have a set UpdateReplacePolicy/DeletionPolicy"
    }
    fn description(&self) -> &str {
        "The default action when replacing/removing a resource is to delete it. \
         This check requires you to explicitly set policies"
    }
    fn severity(&self) -> Severity {
        Severity::Informational
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*"]
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

        // Get the resource type
        let resource_type = match obj.get("Type").and_then(|t| t.as_str()) {
            Some(t) => t,
            None => return vec![],
        };

        if !STATEFUL_TYPES.contains(&resource_type) {
            return vec![];
        }

        let mut errors = Vec::new();

        let has_deletion = obj.get("DeletionPolicy").is_some();
        let has_update = obj.get("UpdateReplacePolicy").is_some();

        if !has_deletion {
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "'DeletionPolicy' is a required property (The default action when \
                         replacing/removing a resource is to delete it. Set explicit \
                         values for stateful resource)"
                    .to_string(),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }
        if !has_update {
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "'UpdateReplacePolicy' is a required property (The default action when \
                         replacing/removing a resource is to delete it. Set explicit \
                         values for stateful resource)"
                    .to_string(),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }

        errors
    }
}

const STATEFUL_TYPES: &[&str] = &[
    "AWS::Backup::BackupVault",
    "AWS::CloudFormation::Stack",
    "AWS::Cognito::UserPool",
    "AWS::DocDB::DBCluster",
    "AWS::DocDB::DBInstance",
    "AWS::DynamoDB::GlobalTable",
    "AWS::DynamoDB::Table",
    "AWS::EC2::Volume",
    "AWS::EFS::FileSystem",
    "AWS::EMR::Cluster",
    "AWS::ElastiCache::CacheCluster",
    "AWS::ElastiCache::ReplicationGroup",
    "AWS::Elasticsearch::Domain",
    "AWS::FSx::FileSystem",
    "AWS::KMS::Key",
    "AWS::Kinesis::Stream",
    "AWS::Logs::LogGroup",
    "AWS::Neptune::DBCluster",
    "AWS::Neptune::DBInstance",
    "AWS::OpenSearchService::Domain",
    "AWS::Organizations::Account",
    "AWS::QLDB::Ledger",
    "AWS::RDS::DBCluster",
    "AWS::RDS::DBInstance",
    "AWS::Redshift::Cluster",
    "AWS::SDB::Domain",
    "AWS::SQS::Queue",
    "AWS::SecretsManager::Secret",
];

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_stateful_with_policies_ok() {
        let yaml = br#"
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
    Properties:
      DBInstanceClass: db.t3.micro
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("DB").unwrap();
        let path = vec!["Resources".to_string(), "DB".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I3011.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_stateful_missing_policies() {
        let yaml = br#"
Resources:
  DB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("DB").unwrap();
        let path = vec!["Resources".to_string(), "DB".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I3011.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 2);
        assert!(errors[0].message.contains("DeletionPolicy"));
        assert!(errors[1].message.contains("UpdateReplacePolicy"));
    }
}

crate::register_cfn_lint_rule!(I3011);
