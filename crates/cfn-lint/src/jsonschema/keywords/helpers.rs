use super::super::ValidationError;
use crate::ast::AstNode;

pub fn err(keyword: &str, message: String, path: &[String], node: &AstNode) -> ValidationError {
    ValidationError::schema_error(keyword, message, path.to_vec(), node.span())
}

pub fn unknown_err(keyword: &str, path: &[String], node: &AstNode) -> ValidationError {
    ValidationError {
        rule_id: None,
        keyword: keyword.to_string(),
        message: "Cannot resolve function".to_string(),
        path: path.to_vec(),
        span: node.span(),
        unknown: true,
        resolved_from_ref: false,
        context: vec![],
        schema_id: None,
    }
}

pub fn has_unknown(errors: &[ValidationError]) -> bool {
    errors.iter().any(|e| e.unknown)
}

/// Structural comparison of an AstNode against a serde_json::Value.
pub fn ast_matches_json(node: &AstNode, value: &serde_json::Value) -> bool {
    match (node, value) {
        (AstNode::String(s), serde_json::Value::String(v)) => s.value == *v,
        (AstNode::Number(n), serde_json::Value::Number(v)) => v
            .as_f64()
            .map_or(false, |f| (n.value - f).abs() < f64::EPSILON),
        (AstNode::Bool(b), serde_json::Value::Bool(v)) => b.value == *v,
        (AstNode::Null(_), serde_json::Value::Null) => true,
        (AstNode::Object(o), serde_json::Value::Object(m)) => {
            o.len() == m.len()
                && o.iter()
                    .all(|(k, v)| m.get(k).map_or(false, |mv| ast_matches_json(v, mv)))
        }
        (AstNode::Array(a), serde_json::Value::Array(v)) => {
            a.elements.len() == v.len()
                && a.elements
                    .iter()
                    .zip(v.iter())
                    .all(|(ae, ve)| ast_matches_json(ae, ve))
        }
        _ => false,
    }
}

pub fn matches_type(node_type: &str, schema_type: &str) -> bool {
    node_type == schema_type || (schema_type == "number" && node_type == "integer")
}

/// Convert an AstNode to a deterministic JSON string for content-based comparison.
pub fn ast_to_json_string(node: &AstNode) -> String {
    match ast_to_json_value(node) {
        Some(v) => serde_json::to_string(&v).unwrap_or_default(),
        None => format!("{}", node),
    }
}

pub fn ast_to_json_value(node: &AstNode) -> Option<serde_json::Value> {
    Some(match node {
        AstNode::String(s) => serde_json::Value::String(s.value.clone()),
        AstNode::Number(n) => {
            serde_json::Number::from_f64(n.value).map(serde_json::Value::Number)?
        }
        AstNode::Bool(b) => serde_json::Value::Bool(b.value),
        AstNode::Null(_) => serde_json::Value::Null,
        AstNode::Object(obj) => {
            let map: serde_json::Map<String, serde_json::Value> = obj
                .iter()
                .filter_map(|(k, v)| ast_to_json_value(v).map(|jv| (k.to_string(), jv)))
                .collect();
            serde_json::Value::Object(map)
        }
        AstNode::Array(arr) => {
            let items: Vec<serde_json::Value> = arr
                .elements
                .iter()
                .filter_map(|e| ast_to_json_value(e))
                .collect();
            serde_json::Value::Array(items)
        }
        AstNode::Function(func) => {
            let mut map = serde_json::Map::new();
            map.insert(func.name.clone(), ast_to_json_value(&func.args)?);
            serde_json::Value::Object(map)
        }
    })
}
