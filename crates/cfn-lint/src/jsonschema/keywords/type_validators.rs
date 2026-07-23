use super::super::{ValidationError, Validator};
use super::helpers::{ast_to_json_value, err, matches_type, python_repr};
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
        serde_json::Value::Array(arr) => arr.iter().any(|t| t.as_str().is_some_and(&type_ok)),
        _ => true,
    };
    if valid {
        vec![]
    } else {
        // Match Python cfn-lint's `type` message: the offending value rendered
        // with Python repr, followed by the accepted types as comma-separated
        // single-quoted names (no brackets). e.g.
        //   {'Nested': 'object'} is not of type 'string', 'boolean'
        let value_repr = ast_to_json_value(node)
            .map(|v| python_repr(&v))
            .unwrap_or_else(|| node_type.to_string());
        let types_repr = match constraint {
            serde_json::Value::Array(arr) => arr
                .iter()
                .filter_map(|t| t.as_str())
                .map(|t| format!("'{}'", t))
                .collect::<Vec<_>>()
                .join(", "),
            serde_json::Value::String(s) => format!("'{}'", s),
            other => format!("{}", other),
        };
        vec![err(
            "type",
            format!("{} is not of type {}", value_repr, types_repr),
            path,
            node,
        )]
    }
}
