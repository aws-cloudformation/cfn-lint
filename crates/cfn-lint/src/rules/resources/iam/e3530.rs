use std::collections::HashMap;
use std::sync::{Arc, LazyLock};

use crate::ast::AstNode;
use crate::context::Context;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::iam_helpers::validate_policy_doc;
use crate::rules::Severity;
use crate::template::Template;

static POLICY_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/iam/policy.json"
    ))
    .unwrap_or_default()
});

static TRUST_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/iam/policy_trust.json"
    ))
    .unwrap_or_default()
});

/// E3530: Validate IAM trust policies.
///
/// IAM trust policies (AssumeRolePolicyDocument) are embedded JSON in CloudFormation.
/// This rule validates those embedded policies against the trust policy schema.
pub struct E3530;

impl CfnLintRule for E3530 {
    fn id(&self) -> &str {
        "E3530"
    }

    fn short_description(&self) -> &str {
        "Validate IAM trust polices"
    }

    fn description(&self) -> &str {
        "IAM trust policies are embedded JSON in CloudFormation. This rule validates those embedded policies."
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let schema = &*TRUST_SCHEMA;
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
            if resource.resource_type != "AWS::IAM::Role" {
                continue;
            }
            let doc = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
                .and_then(|p| p.get("AssumeRolePolicyDocument"))
            {
                Some(d) => d,
                None => continue,
            };
            let base_path = vec![
                "Resources".into(),
                name.clone(),
                "Properties".into(),
                "AssumeRolePolicyDocument".into(),
            ];
            issues.extend(validate_policy_doc(
                doc,
                schema,
                &store,
                &base_path,
                "E3530",
                Some(Arc::clone(&ctx_arc)),
            ));
        }

        issues
    }
}

crate::register_cfn_lint_rule!(E3530);
