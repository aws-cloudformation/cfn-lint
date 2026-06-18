use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::json_schema_rule::validate_schema;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E3679;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/extensions/aws_elasticloadbalancing_loadbalancer/certificate.json"))
        .unwrap_or_default()
});

impl CfnLintRule for E3679 {
    fn id(&self) -> &str { "E3679" }
    fn short_description(&self) -> &str { "Validate ELB protocols that require certificates have a certificate specified" }
    fn description(&self) -> &str { "Validate ELB protocols that require certificates have a certificate specified" }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::ElasticLoadBalancing::LoadBalancer/Properties/Listeners/*",
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
        validate_schema(self.id(), self.short_description(), validator, instance, &SCHEMA, path)
    }
}

crate::register_cfn_lint_rule!(E3679);
