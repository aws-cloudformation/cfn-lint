use std::collections::HashMap;
use std::sync::{Arc, LazyLock};

use crate::ast::AstNode;
use crate::context::Context;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::iam_helpers::validate_policy_doc;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static POLICY_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/other/iam/policy.json")).unwrap_or_default()
});

static RESOURCE_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/iam/policy_resource.json"
    ))
    .unwrap_or_default()
});

/// E3512: Validate resource-based IAM policies.
///
/// Resource-based policies (S3 bucket policies, SQS queue policies, etc.)
/// are embedded JSON in CloudFormation. This rule validates those embedded policies.
pub struct E3512;

/// Resource types and their policy property keys for resource-based policies.
const RESOURCE_PATHS: &[(&str, &str)] = &[
    ("AWS::S3::BucketPolicy", "PolicyDocument"),
    ("AWS::SQS::QueuePolicy", "PolicyDocument"),
    ("AWS::SNS::TopicPolicy", "PolicyDocument"),
    ("AWS::KMS::Key", "KeyPolicy"),
    ("AWS::OpenSearchService::Domain", "AccessPolicies"),
];

impl CfnLintRule for E3512 {
    fn id(&self) -> &str {
        "E3512"
    }

    fn short_description(&self) -> &str {
        "Validate resource based IAM polices"
    }

    fn description(&self) -> &str {
        "IAM resource policies are embedded JSON in CloudFormation. This rule validates those embedded policies."
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let schema = &*RESOURCE_SCHEMA;
        if schema.is_null() {
            return vec![];
        }

        let mut store = HashMap::new();
        store.insert("policy".to_string(), POLICY_SCHEMA.clone());

        let tmpl_arc = Arc::new(template.clone());
        let ctx = Context::new(Arc::clone(&tmpl_arc));
        let ctx_arc = Arc::new(ctx);

        let mut issues = Vec::new();

        for (name, resource) in &template.resources {
            let (_, policy_key) = match RESOURCE_PATHS
                .iter()
                .find(|(rt, _)| *rt == resource.resource_type)
            {
                Some(pair) => pair,
                None => continue,
            };

            let doc = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
                .and_then(|p| p.get(policy_key))
            {
                Some(d) => d,
                None => continue,
            };

            let base_path = vec![
                "Resources".into(),
                name.clone(),
                "Properties".into(),
                policy_key.to_string(),
            ];
            issues.extend(validate_policy_doc(
                doc,
                schema,
                &store,
                &base_path,
                "E3512",
                Some(Arc::clone(&ctx_arc)),
            ));
        }

        issues
    }
}

crate::register_cfn_lint_rule!(E3512);
