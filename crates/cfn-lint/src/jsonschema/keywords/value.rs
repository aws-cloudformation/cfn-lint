use super::super::{ValidationError, Validator};
use super::helpers::{ast_matches_json, ast_to_json_value, err, python_repr};
use crate::ast::AstNode;

fn format_enum_values(constraint: &serde_json::Value) -> String {
    match constraint.as_array() {
        Some(arr) => {
            let items: Vec<String> = arr
                .iter()
                .map(|v| match v {
                    serde_json::Value::String(s) => format!("'{}'", s),
                    serde_json::Value::Number(n) => n.to_string(),
                    serde_json::Value::Bool(b) => b.to_string(),
                    serde_json::Value::Null => "null".to_string(),
                    other => format!("{}", other),
                })
                .collect();
            format!("[{}]", items.join(", "))
        }
        None => format!("{}", constraint),
    }
}

pub fn validate_enum(
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
            return vec![ValidationError {
                rule_id: None,
                message: "Value is an unresolved function".to_string(),
                path: path.to_vec(),
                keyword: String::new(),
                span: node.span(),
                unknown: true,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }
    }
    let variants = match constraint.as_array() {
        Some(a) => a,
        None => return vec![],
    };
    let node_repr = format!("{}", node);
    let matched = variants.iter().any(|v| {
        let v_repr = match v {
            serde_json::Value::String(s) => format!("\"{}\"", s),
            serde_json::Value::Number(n) => format!("{}", n),
            serde_json::Value::Bool(b) => format!("{}", b),
            serde_json::Value::Null => "null".to_string(),
            _ => format!("{}", v),
        };
        if node_repr == v_repr {
            return true;
        }
        // Cross-type: string node "512" should match number enum 512
        if let AstNode::String(s) = node {
            if let Some(n) = v.as_f64() {
                if let Ok(parsed) = s.value.parse::<f64>() {
                    return parsed == n;
                }
            }
        }
        // Cross-type: number node 512 should match string enum "512"
        if let AstNode::Number(n) = node {
            if let Some(s) = v.as_str() {
                if let Ok(parsed) = s.parse::<f64>() {
                    return n.value == parsed;
                }
            }
        }
        false
    });
    if matched {
        vec![]
    } else {
        let value_repr = ast_to_json_value(node)
            .map(|v| python_repr(&v))
            .unwrap_or_else(|| format!("{}", node));
        vec![err(
            "enum",
            format!(
                "{} is not one of {}",
                value_repr,
                format_enum_values(constraint)
            ),
            path,
            node,
        )]
    }
}

pub fn validate_enum_case_insensitive(
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
            return vec![ValidationError {
                rule_id: None,
                message: "Value is an unresolved function".to_string(),
                path: path.to_vec(),
                keyword: String::new(),
                span: node.span(),
                unknown: true,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }
    }
    let variants = match constraint.as_array() {
        Some(a) => a,
        None => return vec![],
    };
    let node_repr = match node {
        AstNode::String(s) => s.value.to_lowercase(),
        _ => format!("{}", node),
    };
    let matched = variants.iter().any(|v| {
        let v_repr = match v {
            serde_json::Value::String(s) => s.to_lowercase(),
            serde_json::Value::Number(n) => format!("{}", n),
            serde_json::Value::Bool(b) => format!("{}", b),
            serde_json::Value::Null => "null".to_string(),
            _ => format!("{}", v),
        };
        node_repr == v_repr
    });
    if matched {
        vec![]
    } else {
        let value_repr = ast_to_json_value(node)
            .map(|v| python_repr(&v))
            .unwrap_or_else(|| format!("{}", node));
        vec![err(
            "enumCaseInsensitive",
            format!(
                "{} is not one of {} (case-insensitive)",
                value_repr,
                format_enum_values(constraint)
            ),
            path,
            node,
        )]
    }
}

pub fn validate_const(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if matches!(node, AstNode::Function(_)) {
        // When functions are disabled (empty list), treat function as literal object
        let functions_disabled = validator
            .context
            .as_ref()
            .and_then(|ctx| ctx.functions.as_ref())
            .map(|f| f.is_empty())
            .unwrap_or(false);
        if functions_disabled {
            let node_json = crate::engine::ast_to_json(node);
            if node_json == *constraint {
                return vec![];
            } else {
                return vec![err(
                    "const",
                    format!("{} was expected", python_repr(constraint)),
                    path,
                    node,
                )];
            }
        }
        return vec![ValidationError {
            message: "Value is an unresolved function".to_string(),
            path: path.to_vec(),
            keyword: String::new(),
            span: node.span(),
            unknown: true,
            ..Default::default()
        }];
    }
    if ast_matches_json(node, constraint) {
        vec![]
    } else {
        vec![err(
            "const",
            format!("{} was expected", python_repr(constraint)),
            path,
            node,
        )]
    }
}
