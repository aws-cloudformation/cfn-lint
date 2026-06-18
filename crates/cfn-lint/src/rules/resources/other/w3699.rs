use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

const REPLICA_MODE_ENGINES: &[&str] = &["oracle", "custom-oracle", "db2"];

pub struct W3699;

impl CfnLintRule for W3699 {
    fn id(&self) -> &str { "W3699" }
    fn short_description(&self) -> &str { "ReplicaMode is ignored for non-Oracle/Db2 engines" }
    fn severity(&self) -> Severity { Severity::Warning }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::RDS::DBInstance/Properties"]
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

        if obj.get("ReplicaMode").is_none() {
            return vec![];
        }

        let engine = match obj.get("Engine").and_then(|n| n.as_str()) {
            Some(e) => e,
            None => return vec![],
        };

        let engine_lower = engine.to_lowercase();
        if REPLICA_MODE_ENGINES.iter().any(|e| engine_lower.starts_with(e)) {
            return vec![];
        }

        let replica_node = obj.get("ReplicaMode").unwrap();
        vec![ValidationError {
            keyword: format!("cfnLint:{}", self.id()),
            message: format!("'ReplicaMode' is ignored when 'Engine' is '{}'", engine),
            path: path.to_vec(),
            span: replica_node.span(),
            ..Default::default()
        }]
    }
}

crate::register_cfn_lint_rule!(W3699);
