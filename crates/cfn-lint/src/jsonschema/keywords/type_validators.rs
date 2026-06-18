use super::super::{ValidationError, Validator};
use super::helpers::{err, matches_type};
use crate::ast::AstNode;

pub fn validate_type(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let AstNode::Function(f) = node {
        let is_allowed = match &validator.context {
            Some(ctx) => match &ctx.functions {
                Some(funcs) => funcs.contains(&f.name),
                None => true,
            },
            None => true,
        };
        if is_allowed {
            return vec![];
        }
    }
    let node_type = node.node_type();

    let type_ok = |schema_type: &str| -> bool {
        if matches_type(node_type, schema_type) {
            return true;
        }
        if validator.strict_types {
            return false;
        }
        // CloudFormation type coercion (relaxed mode)
        match schema_type {
            "string" => matches!(node_type, "integer" | "number" | "boolean"),
            "number" => {
                if node_type == "string" {
                    if let Some(s) = node.as_str() {
                        return s.parse::<f64>().is_ok();
                    }
                }
                false
            }
            "integer" => {
                if node_type == "string" {
                    if let Some(s) = node.as_str() {
                        return s.parse::<f64>().is_ok_and(|v| v.fract() == 0.0);
                    }
                }
                false
            }
            "boolean" => {
                if node_type == "string" {
                    if let Some(s) = node.as_str() {
                        return matches!(s, "true" | "True" | "TRUE" | "false" | "False" | "FALSE");
                    }
                }
                false
            }
            _ => false,
        }
    };

    let valid = match constraint {
        serde_json::Value::String(s) => type_ok(s),
        serde_json::Value::Array(arr) => arr
            .iter()
            .any(|t| t.as_str().is_some_and(|s| type_ok(s))),
        _ => true,
    };
    if valid {
        vec![]
    } else {
        vec![err(
            "type",
            format!("{} is not of type {}", node_type, constraint),
            path,
            node,
        )]
    }
}
