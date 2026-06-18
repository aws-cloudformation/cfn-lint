use super::super::{ValidationError, Validator};
use super::helpers::{err, ast_to_json_string};
use crate::ast::AstNode;
use std::collections::HashSet;

pub fn validate_items(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let arr = match node.as_array() {
        Some(a) => a,
        None => return vec![],
    };
    let mut errors = Vec::new();
    for (i, elem) in arr.elements.iter().enumerate() {
        let mut child_path = path.to_vec();
        child_path.push(i.to_string());
        errors.extend(validator.validate_schema(elem, constraint, &child_path));
    }
    errors
}

pub fn validate_min_items(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (Some(arr), Some(min)) = (node.as_array(), constraint.as_u64()) {
        if arr.elements.len() < min as usize {
            return vec![err(
                "minItems",
                format!("expected minimum item count: {}, found: {}", min, arr.elements.len()),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_max_items(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (Some(arr), Some(max)) = (node.as_array(), constraint.as_u64()) {
        if arr.elements.len() > max as usize {
            return vec![err(
                "maxItems",
                format!(
                    "expected maximum item count: {}, found: {}",
                    max,
                    arr.elements.len()
                ),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_max_unique_items(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (Some(arr), Some(max)) = (node.as_array(), constraint.as_u64()) {
        let unique: HashSet<String> = arr.elements.iter().map(|e| format!("{}", e)).collect();
        if unique.len() > max as usize {
            return vec![err(
                "maxUniqueItems",
                format!(
                    "expected maximum unique item count: {}, found: {}",
                    max,
                    unique.len()
                ),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_unique_items(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if constraint.as_bool() != Some(true) {
        return vec![];
    }
    let arr = match node.as_array() {
        Some(a) => a,
        None => return vec![],
    };
    let mut seen = HashSet::new();
    for elem in &arr.elements {
        let repr = ast_to_json_string(elem);
        if !seen.insert(repr) {
            return vec![err(
                "uniqueItems",
                "Array items are not unique".to_string(),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_contains(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let arr = match node.as_array() {
        Some(a) => a,
        None => return vec![],
    };
    let has_match = arr
        .elements
        .iter()
        .any(|elem| validator.validate_schema(elem, constraint, path).is_empty());
    if !has_match {
        return vec![err(
            "contains",
            "Array does not contain items matching the given schema".to_string(),
            path,
            node,
        )];
    }
    vec![]
}

pub fn validate_prefix_items(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (arr, schemas) = match (node.as_array(), constraint.as_array()) {
        (Some(a), Some(s)) => (a, s),
        _ => return vec![],
    };
    let mut errors = Vec::new();
    for (i, (elem, sub_schema)) in arr.elements.iter().zip(schemas.iter()).enumerate() {
        let mut child_path = path.to_vec();
        child_path.push(i.to_string());
        for mut e in validator.validate_schema(elem, sub_schema, &child_path) {
            e.keyword = "prefixItems".to_string();
            errors.push(e);
        }
    }
    errors
}

pub fn validate_unique_keys(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (arr, keys) = match (node.as_array(), constraint.as_array()) {
        (Some(a), Some(k)) => (a, k),
        _ => return vec![],
    };
    let key_names: Vec<&str> = keys.iter().filter_map(|k| k.as_str()).collect();
    let mut seen: Vec<Vec<String>> = Vec::new();
    for elem in &arr.elements {
        let obj = match elem.as_object() {
            Some(o) => o,
            None => continue,
        };
        let vals: Vec<String> = key_names
            .iter()
            .map(|k| {
                obj.get(*k)
                    .map(|v| ast_to_json_string(v))
                    .unwrap_or_default()
            })
            .collect();
        // Skip items where any key is missing — missing keys don't count as duplicates
        if key_names.iter().any(|k| !obj.contains_key(*k)) {
            continue;
        }
        if seen.contains(&vals) {
            return vec![err(
                "uniqueKeys",
                format!("array items are not unique for keys {:?}", constraint),
                path,
                node,
            )];
        }
        seen.push(vals);
    }
    vec![]
}
