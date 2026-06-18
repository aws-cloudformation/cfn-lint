use std::collections::HashMap;
use std::sync::{Arc, LazyLock};

use crate::ast::AstNode;
use crate::context::Context;
use crate::engine::expand_fn_if_branches;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::iam_helpers::validate_policy_doc;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static POLICY_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../../data/schemas/other/iam/policy.json")).unwrap_or_default()
});

static IDENTITY_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/iam/policy_identity.json"
    ))
    .unwrap_or_default()
});

/// E3510: Validate identity-based IAM policies.
///
/// IAM identity policies are embedded JSON in CloudFormation templates.
/// This rule validates those embedded policies against the IAM policy schema.
pub struct E3510;

/// Resource types and their policy property paths for identity policies.
/// (resource_type, property_key, is_array)
const IDENTITY_PATHS: &[(&str, &str, bool)] = &[
    ("AWS::IAM::Policy", "PolicyDocument", false),
    ("AWS::IAM::ManagedPolicy", "PolicyDocument", false),
    ("AWS::IAM::Role", "Policies", true),
    ("AWS::IAM::User", "Policies", true),
    ("AWS::IAM::Group", "Policies", true),
    ("AWS::SSO::PermissionSet", "InlinePolicy", false),
    ("AWS::IAM::UserPolicy", "PolicyDocument", false),
    ("AWS::IAM::RolePolicy", "PolicyDocument", false),
    ("AWS::IAM::GroupPolicy", "PolicyDocument", false),
];

impl CfnLintRule for E3510 {
    fn id(&self) -> &str {
        "E3510"
    }

    fn short_description(&self) -> &str {
        "Validate identity based IAM polices"
    }

    fn description(&self) -> &str {
        "IAM identity policies are embedded JSON in CloudFormation. This rule validates those embedded policies."
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let schema = &*IDENTITY_SCHEMA;
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
            let (_, prop_key, is_array) = match IDENTITY_PATHS
                .iter()
                .find(|(rt, _, _)| *rt == resource.resource_type)
            {
                Some(entry) => entry,
                None => continue,
            };

            let props = match root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
            {
                Some(p) => p,
                None => continue,
            };

            if *is_array {
                let policies = match props.get(prop_key) {
                    Some(p) => p,
                    None => continue,
                };
                if policies.as_function().is_some() {
                    continue;
                }
                let arr = match policies.as_array() {
                    Some(a) => a,
                    None => continue,
                };
                for (i, policy) in arr.elements.iter().enumerate() {
                    let policy_branches = expand_fn_if_branches(
                        policy,
                        vec![
                            "Resources".into(),
                            name.clone(),
                            "Properties".into(),
                            prop_key.to_string(),
                            i.to_string(),
                        ],
                    );
                    for (branch_node, branch_path) in &policy_branches {
                        if branch_node.as_function().is_some() {
                            continue;
                        }
                        let doc = match branch_node.get("PolicyDocument") {
                            Some(d) => d,
                            None => continue,
                        };
                        let mut base_path = branch_path.clone();
                        base_path.push("PolicyDocument".into());
                        issues.extend(validate_policy_doc(
                            doc,
                            schema,
                            &store,
                            &base_path,
                            "E3510",
                            Some(Arc::clone(&ctx_arc)),
                        ));
                    }
                }
            } else {
                let branches = expand_fn_if_branches(
                    props,
                    vec!["Resources".into(), name.clone(), "Properties".into()],
                );
                for (branch_node, branch_path) in &branches {
                    let doc = match branch_node.get(prop_key) {
                        Some(d) => d,
                        None => continue,
                    };
                    let mut base_path = branch_path.clone();
                    base_path.push(prop_key.to_string());
                    issues.extend(validate_policy_doc(
                        doc,
                        schema,
                        &store,
                        &base_path,
                        "E3510",
                        Some(Arc::clone(&ctx_arc)),
                    ));
                }
            }
        }

        issues
    }
}

crate::register_cfn_lint_rule!(E3510);
