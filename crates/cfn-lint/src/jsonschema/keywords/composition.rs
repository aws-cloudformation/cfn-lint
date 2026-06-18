use super::super::{ValidationError, Validator};
use super::helpers::{err, unknown_err, has_unknown};
use crate::ast::AstNode;

pub fn validate_all_of(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let schemas = match constraint.as_array() {
        Some(a) => a,
        None => return vec![],
    };
    let mut errors = Vec::new();
    let mut found_unknown = false;
    for sub in schemas {
        let errs = validator.validate_schema(node, sub, path);
        if has_unknown(&errs) {
            found_unknown = true;
            // Still collect non-unknown errors — real violations shouldn't be discarded
            errors.extend(errs.into_iter().filter(|e| !e.unknown));
        } else {
            errors.extend(errs);
        }
    }
    if found_unknown && errors.is_empty() {
        errors.push(unknown_err("allOf", path, node));
    }
    errors
}

pub fn validate_any_of(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let schemas = match constraint.as_array() {
        Some(a) => a,
        None => return vec![],
    };
    let mut found_unknown = false;
    let mut all_errors: Vec<ValidationError> = Vec::new();
    for sub in schemas {
        let errs = validator.validate_schema(node, sub, path);
        if errs.is_empty() {
            return vec![];
        }
        if has_unknown(&errs) {
            found_unknown = true;
        }
        all_errors.extend(errs);
    }
    if found_unknown {
        return vec![unknown_err("anyOf", path, node)];
    }
    // Surface individual sub-errors via context (mirrors Python)
    let mut e = err(
        "anyOf",
        "Value does not match any of the schemas in anyOf".to_string(),
        path,
        node,
    );
    e.context = all_errors.into_iter().filter(|e| !e.unknown).collect();
    vec![e]
}

pub fn validate_one_of(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let schemas = match constraint.as_array() {
        Some(a) => a,
        None => return vec![],
    };
    let mut match_count = 0;
    let mut found_unknown = false;
    let mut all_errors: Vec<ValidationError> = Vec::new();
    for sub in schemas {
        let errs = validator.validate_schema(node, sub, path);
        if errs.is_empty() {
            match_count += 1;
        } else if has_unknown(&errs) {
            found_unknown = true;
        } else {
            all_errors.extend(errs);
        }
    }
    if match_count == 1 && !found_unknown {
        vec![]
    } else if found_unknown {
        vec![unknown_err("oneOf", path, node)]
    } else {
        let mut e = err(
            "oneOf",
            format!(
                "Value must match exactly one schema in oneOf, matched {}",
                match_count
            ),
            path,
            node,
        );
        e.context = all_errors;
        vec![e]
    }
}

pub fn validate_not(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let errs = validator.validate_schema(node, constraint, path);
    if has_unknown(&errs) {
        return vec![unknown_err("not", path, node)];
    }
    if errs.is_empty() {
        vec![err(
            "not",
            "Value must not match the schema in not".to_string(),
            path,
            node,
        )]
    } else {
        vec![]
    }
}

pub fn validate_if_then_else(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    // Evaluate the if-condition without cfnLint rules to avoid contaminating
    // the structural check with errors from external keyword rule dispatch.
    let if_validator = validator.without_cfn_lint_rules();
    let if_errors = if_validator.validate_schema(node, constraint, path);
    if has_unknown(&if_errors) {
        return vec![unknown_err("if", path, node)];
    }
    if if_errors.is_empty() {
        if let Some(then_schema) = schema.get("then") {
            return validator.validate_schema(node, then_schema, path);
        }
    } else {
        if let Some(else_schema) = schema.get("else") {
            return validator.validate_schema(node, else_schema, path);
        }
    }
    vec![]
}
