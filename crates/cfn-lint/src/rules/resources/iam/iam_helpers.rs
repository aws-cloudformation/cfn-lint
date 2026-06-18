//! Shared helpers for IAM policy validation rules (E3510, E3512, E3513, E3530).

use std::collections::{HashMap, HashSet};
use std::sync::Arc;

use crate::ast::AstNode;
use crate::context::Context;
use crate::engine::flatten_validation_errors;
use crate::jsonschema::ValidationError;
use crate::jsonschema::Validator;
use crate::rules::Severity;

/// Validate a policy document AstNode against an IAM policy schema.
/// Skips function nodes. Returns issues tagged with the given rule_id.
pub(crate) fn validate_policy_doc(
    doc: &AstNode,
    schema: &serde_json::Value,
    store: &HashMap<String, serde_json::Value>,
    base_path: &[String],
    rule_id: &str,
    context: Option<Arc<Context>>,
) -> Vec<crate::jsonschema::ValidationError> {
    if doc.as_function().is_some() || doc.as_str().is_some() {
        return vec![];
    }
    let mut validator = Validator::new_with_store(schema.clone(), store.clone());
    validator.context = context;
    let errors = validator.validate(doc, schema, base_path);
    let mut seen = HashSet::new();
    errors
        .into_iter()
        .flat_map(flatten_validation_errors)
        .filter(|err| {
            !err.unknown
                && (!err.keyword.starts_with("fn_")
                    || (err.keyword == "fn_getatt" && err.message.contains("is not one of")))
        })
        .filter_map(|err| {
            let key = (err.path.clone(), err.message.clone());
            if seen.insert(key) {
                Some(err)
            } else {
                None
            }
        })
        .map(|err| {
            // Preserve resolved function rule IDs (W1031, W1032, etc.)
            // Map fn_getatt errors to E1010
            let effective_rule = if err.keyword == "fn_getatt" {
                "E1010"
            } else if err.keyword.starts_with('W') || err.keyword.starts_with('E') {
                if err.keyword.len() <= 5 && err.keyword[1..].chars().all(|c| c.is_ascii_digit()) {
                    err.keyword.as_str()
                } else {
                    rule_id
                }
            } else {
                rule_id
            };
            ValidationError {
                rule_id: Some(effective_rule.to_string()),
                message: err.message,
                path: err.path,
                keyword: err.keyword,
                span: err.span,
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }
        })
        .collect()
}
