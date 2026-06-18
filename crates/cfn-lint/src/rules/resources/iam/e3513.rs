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

static ECR_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/iam/policy_resource_ecr.json"
    ))
    .unwrap_or_default()
});

/// E3513: Validate ECR repository policy.
///
/// Private ECR repositories have a resource-based policy (RepositoryPolicyText).
/// This rule validates those policies against the ECR-specific IAM policy schema.
pub struct E3513;

impl CfnLintRule for E3513 {
    fn id(&self) -> &str {
        "E3513"
    }

    fn short_description(&self) -> &str {
        "Validate ECR repository policy"
    }

    fn description(&self) -> &str {
        "Private ECR repositories have a policy. This rule validates those policies."
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let schema = &*ECR_SCHEMA;
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
            if resource.resource_type != "AWS::ECR::Repository" {
                continue;
            }
            let doc = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
                .and_then(|p| p.get("RepositoryPolicyText"))
            {
                Some(d) => d,
                None => continue,
            };
            let base_path = vec![
                "Resources".into(),
                name.clone(),
                "Properties".into(),
                "RepositoryPolicyText".into(),
            ];
            issues.extend(validate_policy_doc(
                doc,
                schema,
                &store,
                &base_path,
                "E3513",
                Some(Arc::clone(&ctx_arc)),
            ));
        }

        issues
    }
}

crate::register_cfn_lint_rule!(E3513);
