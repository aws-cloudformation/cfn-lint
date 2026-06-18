use super::super::{ValidationError, Validator};
use super::helpers::err;
use crate::ast::AstNode;
use regex::Regex;

pub fn validate_min_length(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (AstNode::String(s), Some(min)) = (node, constraint.as_u64()) {
        if s.value.len() < min as usize {
            return vec![err(
                "minLength",
                format!("expected minimum length: {}, found: {}", min, s.value.len()),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_max_length(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (AstNode::String(s), Some(max)) = (node, constraint.as_u64()) {
        if s.value.len() > max as usize {
            return vec![err(
                "maxLength",
                format!("expected maximum length: {}, found: {}", max, s.value.len()),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_pattern(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (AstNode::String(s), Some(pat)) = (node, constraint.as_str()) {
        let matched = if let Ok(re) = Regex::new(pat) {
            re.is_match(&s.value)
        } else if let Ok(re) = fancy_regex::Regex::new(pat) {
            re.is_match(&s.value).unwrap_or(false)
        } else {
            return vec![];
        };
        if !matched {
            return vec![err(
                "pattern",
                format!("'{}' does not match '{}'", s.value, pat),
                path,
                node,
            )];
        }
    }
    vec![]
}
