use super::super::{ValidationError, Validator};
use super::helpers::{compile_pattern, err};
use crate::ast::AstNode;
use std::collections::HashSet;

pub fn validate_properties(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (obj, props) = match (node.as_object(), constraint.as_object()) {
        (Some(o), Some(p)) => (o, p),
        _ => return vec![],
    };
    let mut errors = Vec::new();
    for (key, prop_schema) in props {
        if let Some(value) = obj.get(key) {
            let mut child_path = path.to_vec();
            child_path.push(key.clone());
            errors.extend(validator.validate_schema(value, prop_schema, &child_path));
        }
    }
    errors
}

pub fn validate_required(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (obj, required) = match (node.as_object(), constraint.as_array()) {
        (Some(o), Some(r)) => (o, r),
        _ => return vec![],
    };
    let mut errors = Vec::new();
    for req in required {
        if let Some(name) = req.as_str() {
            let is_present = match obj.get(name) {
                None => false,
                Some(AstNode::Null(_)) => false,
                Some(v) => !is_ref_no_value(v, validator),
            };
            if !is_present {
                errors.push(err(
                    "required",
                    format!("'{}' is a required property", name),
                    path,
                    node,
                ));
            }
        }
    }
    errors
}

/// Check if a node is `Ref: AWS::NoValue`.
fn is_ref_no_value(node: &AstNode, _validator: &Validator) -> bool {
    matches!(node, AstNode::Function(func) if func.name == "Ref" && func.args.as_str() == Some("AWS::NoValue"))
}

pub fn validate_additional_properties(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let obj = match node.as_object() {
        Some(o) => o,
        None => return vec![],
    };

    let defined: HashSet<&str> = schema
        .get("properties")
        .and_then(|p| p.as_object())
        .map(|p| p.keys().map(|k| k.as_str()).collect())
        .unwrap_or_default();

    let pattern_strings: Vec<&str> = schema
        .get("patternProperties")
        .and_then(|p| p.as_object())
        .map(|p| p.keys().map(|k| k.as_str()).collect())
        .unwrap_or_default();

    let mut errors = Vec::new();
    for key in obj.keys() {
        if defined.contains(key) {
            continue;
        }
        // Non-string keys (numbers, bools) cannot match string patterns
        if !obj.is_non_string_key(key) {
            let matches_pattern = pattern_strings.iter().any(|pat| {
                compile_pattern(pat)
                    .map(|re| re.is_match(key))
                    .unwrap_or(false)
            });
            if matches_pattern {
                continue;
            }
        }
        // This key is additional
        match constraint {
            serde_json::Value::Bool(false) => {
                let prop_node = obj.get(key).unwrap_or(node);
                let message = if !pattern_strings.is_empty() {
                    let patterns = schema
                        .get("patternProperties")
                        .and_then(|p| p.as_object())
                        .map(|p| {
                            p.keys()
                                .map(|k| format!("'{}'", k))
                                .collect::<Vec<_>>()
                                .join(", ")
                        })
                        .unwrap_or_default();
                    format!("'{}' does not match any of the regexes: {}", key, patterns)
                } else {
                    format!(
                        "Additional properties are not allowed ('{}' was unexpected)",
                        key
                    )
                };
                errors.push(err("additionalProperties", message, path, prop_node));
            }
            serde_json::Value::Object(_) => {
                let mut child_path = path.to_vec();
                child_path.push(key.to_string());
                errors.extend(validator.validate_schema(
                    obj.get(key).unwrap(),
                    constraint,
                    &child_path,
                ));
            }
            _ => {}
        }
    }
    errors
}

pub fn validate_pattern_properties(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (obj, patterns) = match (node.as_object(), constraint.as_object()) {
        (Some(o), Some(p)) => (o, p),
        _ => return vec![],
    };
    let mut errors = Vec::new();
    for (pattern, prop_schema) in patterns {
        // A pattern that neither engine can compile matches nothing.
        let re = match compile_pattern(pattern) {
            Some(re) => re,
            None => continue,
        };
        for (key, value) in obj.iter() {
            // Non-string keys cannot match string patterns
            if obj.is_non_string_key(key) {
                continue;
            }
            if re.is_match(key) {
                let mut child_path = path.to_vec();
                child_path.push(key.to_string());
                errors.extend(validator.validate_schema(value, prop_schema, &child_path));
            }
        }
    }
    errors
}

pub fn validate_dependent_required(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (obj, deps) = match (node.as_object(), constraint.as_object()) {
        (Some(o), Some(d)) => (o, d),
        _ => return vec![],
    };
    let mut errors = Vec::new();
    for (trigger, required) in deps {
        if !obj.contains_key(trigger) {
            continue;
        }
        if let Some(arr) = required.as_array() {
            for req in arr {
                if let Some(name) = req.as_str() {
                    if !obj.contains_key(name) {
                        errors.push(err(
                            "dependentRequired",
                            format!(
                                "Property \"{}\" is required when \"{}\" is present",
                                name, trigger
                            ),
                            path,
                            node,
                        ));
                    }
                }
            }
        }
    }
    errors
}

pub fn validate_dependent_excluded(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (obj, deps) = match (node.as_object(), constraint.as_object()) {
        (Some(o), Some(d)) => (o, d),
        _ => return vec![],
    };
    let mut errors = Vec::new();
    for (trigger, excluded) in deps {
        if !obj.contains_key(trigger) {
            continue;
        }
        if let Some(arr) = excluded.as_array() {
            for exc in arr {
                if let Some(name) = exc.as_str() {
                    if obj.contains_key(name) {
                        let mut exc_path = path.to_vec();
                        exc_path.push(name.to_string());
                        errors.push(err(
                            "dependentExcluded",
                            format!("\"{}\" should not be included with \"{}\"", name, trigger),
                            &exc_path,
                            node,
                        ));
                    }
                }
            }
        }
    }
    errors
}

pub fn validate_max_properties(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (Some(obj), Some(max)) = (node.as_object(), constraint.as_u64()) {
        if obj.len() > max as usize {
            return vec![err(
                "maxProperties",
                format!(
                    "expected maximum property count: {}, found: {}",
                    max,
                    obj.len()
                ),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_min_properties(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (Some(obj), Some(min)) = (node.as_object(), constraint.as_u64()) {
        if obj.len() < min as usize {
            return vec![err(
                "minProperties",
                format!(
                    "expected minimum property count: {}, found: {}",
                    min,
                    obj.len()
                ),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_property_names(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let obj = match node.as_object() {
        Some(o) => o,
        None => return vec![],
    };
    let mut errors = Vec::new();
    for key in obj.keys() {
        let key_node = AstNode::String(crate::ast::StringNode {
            value: key.to_string(),
            span: node.span(),
        });
        let mut child_path = path.to_vec();
        child_path.push(key.to_string());
        errors.extend(validator.validate_schema(&key_node, constraint, &child_path));
    }
    errors
}

pub fn validate_required_xor(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (obj, required) = match (node.as_object(), constraint.as_array()) {
        (Some(o), Some(r)) => (o, r),
        _ => return vec![],
    };
    let matches: Vec<&str> = required
        .iter()
        .filter_map(|v| v.as_str())
        .filter(|name| {
            obj.get(name).is_some_and(|v| {
                // Ref AWS::NoValue means absent
                !matches!(v, AstNode::Function(f) if f.name == "Ref" && f.args.as_str() == Some("AWS::NoValue"))
            })
        })
        .collect();
    if matches.is_empty() {
        return vec![err(
            "requiredXor",
            format!("Only one of {:?} is a required property", constraint),
            path,
            node,
        )];
    }
    if matches.len() > 1 {
        return matches
            .iter()
            .map(|m| {
                let mut child_path = path.to_vec();
                child_path.push(m.to_string());
                err(
                    "requiredXor",
                    format!("Only one of {:?} is a required property", constraint),
                    &child_path,
                    node,
                )
            })
            .collect();
    }
    vec![]
}

pub fn validate_required_or(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let (obj, required) = match (node.as_object(), constraint.as_array()) {
        (Some(o), Some(r)) => (o, r),
        _ => return vec![],
    };
    let has_match = required
        .iter()
        .filter_map(|v| v.as_str())
        .any(|name| {
            obj.get(name).is_some_and(|v| {
                !matches!(v, AstNode::Function(f) if f.name == "Ref" && f.args.as_str() == Some("AWS::NoValue"))
            })
        });
    if !has_match {
        return vec![err(
            "requiredOr",
            format!("One of {:?} is a required property", constraint),
            path,
            node,
        )];
    }
    vec![]
}
