use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3035: Check DeletionPolicy values for Resources.
///
/// Dynamically builds a schema with the correct enum values based on the
/// resource type (Snapshot support).
pub struct E3035;

pub const SNAPSHOT_TYPES: &[&str] = &[
    "AWS::DocDB::DBCluster",
    "AWS::EC2::Volume",
    "AWS::ElastiCache::CacheCluster",
    "AWS::ElastiCache::ReplicationGroup",
    "AWS::Neptune::DBCluster",
    "AWS::RDS::DBCluster",
    "AWS::RDS::DBInstance",
    "AWS::Redshift::Cluster",
];

impl CfnLintRule for E3035 {
    fn id(&self) -> &str {
        "E3035"
    }
    fn short_description(&self) -> &str {
        "Check DeletionPolicy values for Resources"
    }
    fn description(&self) -> &str {
        "Check that the DeletionPolicy values are valid"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/DeletionPolicy"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        // Get the resource name from path: Resources/<name>/DeletionPolicy
        let resource_name = match path.get(1) {
            Some(n) => n.as_str(),
            None => return vec![],
        };

        // Determine resource type from template context
        let resource_type = if let Some(ctx) = validator.context() {
            ctx.template
                .resources
                .get(resource_name)
                .map(|r| r.resource_type.as_str())
                .unwrap_or("")
        } else {
            ""
        };

        let mut valid = vec!["Delete", "Retain", "RetainExceptOnCreate"];
        if SNAPSHOT_TYPES.contains(&resource_type) {
            valid.push("Snapshot");
        }
        let schema = serde_json::json!({"type": "string", "enum": valid});

        // Only allow functions that CFN supports in DeletionPolicy
        let evolved = validator.evolve(crate::jsonschema::ContextEvolution {
            functions: Some(vec![
                "Fn::Sub".to_string(),
                "Fn::Select".to_string(),
                "Fn::FindInMap".to_string(),
                "Fn::If".to_string(),
                "Ref".to_string(),
            ]),
            ..Default::default()
        });
        let v = evolved.without_cfn_lint_rules();
        v.validate_schema(instance, &schema, path)
            .into_iter()
            .filter(|e| !e.unknown)
            .map(|mut err| {
                err.keyword = format!("cfnLint:{}", self.id());
                err
            })
            .collect()
    }
}

crate::register_cfn_lint_rule!(E3035);
