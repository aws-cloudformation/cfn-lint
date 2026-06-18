use std::sync::{Arc, LazyLock};

use crate::ast::AstNode;
use crate::context::Context;
use crate::engine::{check_equals_comma_delimited, flatten_validation_errors};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::template::Template;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../data/schemas/other/conditions/conditions.json"
    ))
    .unwrap_or_default()
});

/// E8001: Conditions have appropriate properties.
pub struct E8001;

impl CfnLintRule for E8001 {
    fn id(&self) -> &str {
        "E8001"
    }
    fn short_description(&self) -> &str {
        "Conditions have appropriate properties"
    }
    fn description(&self) -> &str {
        "Check that each condition value is a valid condition function"
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
        let conditions = match root.get("Conditions") {
            Some(n) => n,
            None => return vec![],
        };

        let mut issues = Vec::new();

        // Basic schema validation (catches type errors, extra properties, etc.)
        // Use a validator without context — function nodes will be skipped (unknown).
        // Errors with rule-ID keywords (E8003, W8003, etc.) are handled by the second pass.
        let validator = Validator::new(SCHEMA.clone());
        let base_path = vec!["Conditions".to_string()];
        issues.extend(
            validator
                .validate(conditions, &SCHEMA, &base_path)
                .into_iter()
                .filter(|e| !e.unknown)
                .filter(|e| {
                    // Skip errors from function handlers (rule-ID-style keywords)
                    // These are caught by the context-aware second pass below
                    let kw = &e.keyword;
                    !(kw.len() <= 5
                        && (kw.starts_with('E') || kw.starts_with('W') || kw.starts_with('I'))
                        && kw[1..].chars().all(|c| c.is_ascii_digit()))
                })
                .map(|err| ValidationError {
                    rule_id: Some("E8001".to_string()),
                    message: err.message,
                    path: err.path,
                    span: err.span,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }),
        );

        // Context-aware validation with condition functions allowed.
        // This catches E8003/E8004/W8xxx errors produced by function handlers.
        let tmpl_arc = Arc::new(template.clone());
        let ctx = Context::new(Arc::clone(&tmpl_arc)).evolve(crate::context::ContextOptions {
            functions: Some(vec![
                "Fn::Equals".to_string(),
                "Fn::And".to_string(),
                "Fn::Or".to_string(),
                "Fn::Not".to_string(),
                "Condition".to_string(),
            ]),
            ..Default::default()
        });

        let ctx_validator = Validator::new_with_context(serde_json::json!({}), Arc::new(ctx));
        let path = vec!["Conditions".to_string()];
        let errs = ctx_validator.validate(conditions, &SCHEMA, &path);
        for e in errs.into_iter().flat_map(flatten_validation_errors) {
            if e.unknown {
                continue;
            }
            // Only keep E8xxx/W8xxx errors produced by function handlers.
            if e.keyword.starts_with("E8") || e.keyword.starts_with("W8") {
                let rule_id = e.keyword.clone();
                let severity = if rule_id.starts_with('W') {
                    Severity::Warning
                } else {
                    Severity::Error
                };
                issues.push(ValidationError {
                    rule_id: Some(rule_id),
                    message: e.message,
                    path: e.path,
                    span: e.span,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
            }
        }

        // Check for Ref to CommaDelimitedList parameters inside Fn::Equals
        if let Some(conds_obj) = conditions.as_object() {
            for cond_node in conds_obj.values() {
                check_equals_comma_delimited(cond_node, template, &mut issues);
            }
        }

        issues
    }
}

crate::register_cfn_lint_rule!(E8001);
