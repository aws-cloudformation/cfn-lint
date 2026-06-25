use crate::ast::{
    ArrayNode, AstNode, BoolNode, NullNode, NumberNode, ObjectEntry, ObjectNode, Span, StringNode,
};

pub(crate) fn follow_pointer<'a>(node: &'a AstNode, pointer: &str) -> Option<&'a AstNode> {
    let parts: Vec<&str> = pointer.trim_start_matches('/').split('/').collect();
    let mut current = node;
    for part in parts {
        current = current.get(part)?;
    }
    Some(current)
}

pub(crate) fn ref_to_resource_name(node: &AstNode) -> Option<String> {
    match node {
        AstNode::Function(func) => match func.name.as_str() {
            "Ref" => func.args.as_str().map(String::from),
            "Fn::GetAtt" => match func.args.as_ref() {
                AstNode::Array(arr) => arr.elements.first()?.as_str().map(String::from),
                AstNode::String(s) => s.value.split('.').next().map(String::from),
                _ => None,
            },
            _ => None,
        },
        _ => None,
    }
}

pub(crate) fn ast_to_json(node: &AstNode) -> serde_json::Value {
    match node {
        AstNode::String(s) => serde_json::Value::String(s.value.clone()),
        AstNode::Number(n) => serde_json::json!(n.value),
        AstNode::Bool(b) => serde_json::Value::Bool(b.value),
        AstNode::Null(_) => serde_json::Value::Null,
        AstNode::Object(o) => {
            let map: serde_json::Map<String, serde_json::Value> = o
                .iter()
                .map(|(k, v)| (k.to_string(), ast_to_json(v)))
                .collect();
            serde_json::Value::Object(map)
        }
        AstNode::Array(a) => serde_json::Value::Array(a.elements.iter().map(ast_to_json).collect()),
        AstNode::Function(f) => {
            let mut map = serde_json::Map::new();
            map.insert(f.name.clone(), ast_to_json(&f.args));
            serde_json::Value::Object(map)
        }
    }
}

pub(crate) fn format_node_short(node: &AstNode) -> String {
    match node {
        AstNode::Function(f) => {
            if let Some(s) = f.args.as_str() {
                format!("{{'{}': '{}'}}", f.name, s)
            } else {
                format!("{{'{}': ...}}", f.name)
            }
        }
        AstNode::String(s) => format!("'{}'", s.value),
        AstNode::Null(_) => "None".to_string(),
        _ => format!("{:?}", ast_to_json(node)),
    }
}

pub(crate) fn json_to_ast(val: &serde_json::Value) -> AstNode {
    match val {
        serde_json::Value::String(s) => AstNode::String(StringNode {
            value: s.clone(),
            span: Span::default(),
        }),
        serde_json::Value::Number(n) => AstNode::Number(NumberNode {
            value: n.as_f64().unwrap_or(0.0),
            span: Span::default(),
        }),
        serde_json::Value::Bool(b) => AstNode::Bool(BoolNode {
            value: *b,
            span: Span::default(),
        }),
        serde_json::Value::Null => AstNode::Null(NullNode {
            span: Span::default(),
        }),
        serde_json::Value::Object(map) => {
            let entries = map
                .iter()
                .map(|(k, v)| ObjectEntry {
                    key_node: AstNode::String(StringNode {
                        value: k.clone(),
                        span: Span::default(),
                    }),
                    key: k.clone(),
                    value: json_to_ast(v),
                    key_span: Span::default(),
                })
                .collect();
            AstNode::Object(ObjectNode {
                entries,
                span: Span::default(),
            })
        }
        serde_json::Value::Array(arr) => AstNode::Array(ArrayNode {
            elements: arr.iter().map(json_to_ast).collect(),
            span: Span::default(),
        }),
    }
}

pub(crate) fn flatten_validation_errors(
    err: crate::jsonschema::ValidationError,
) -> Vec<crate::jsonschema::ValidationError> {
    if err.context.is_empty() {
        return vec![err];
    }
    // anyOf/oneOf: emit the top-level error (→ E3017/E3024) AND the flattened
    // sub-errors. Python emits both: the anyOf violation AND individual required
    // failures from each failing branch.
    if err.keyword == "anyOf" || err.keyword == "oneOf" {
        let top = crate::jsonschema::ValidationError {
            context: vec![],
            ..err.clone()
        };
        let mut result = vec![top];
        result.extend(err.context.into_iter().flat_map(flatten_validation_errors));
        return result;
    }
    let context = err.context;
    let flattened: Vec<_> = context
        .into_iter()
        .flat_map(flatten_validation_errors)
        .collect();
    if flattened.is_empty() {
        return vec![crate::jsonschema::ValidationError {
            context: vec![],
            ..err
        }];
    }
    flattened
}
