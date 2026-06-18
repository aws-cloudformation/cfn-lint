use crate::ast::AstNode;

use super::{ast_to_json, follow_pointer};

/// Resolve `$data` and `$lookup` references in a JSON schema.
///
/// `$data`: `{"$data": "/path"}` → replaced with the value at that JSON pointer in `gathered`.
///
/// `$lookup`: `{"$lookup": {"key": <expr>, "map": {…}}}` → resolve `key` recursively
/// (it may contain `$data`), then look it up in `map`. If the resolved key is a string
/// present in the map, the entire `$lookup` object is replaced with the mapped value.
/// Otherwise it is replaced with `null`.
///
/// When a data-bearing keyword (`const`, `enum`, `pattern`, numeric constraints) resolves
/// to `null`, the keyword is dropped from the schema so it doesn't cause false positives.
pub(crate) fn resolve_data_refs(
    schema: &serde_json::Value,
    gathered: &AstNode,
) -> serde_json::Value {
    resolve_data_value(schema, gathered)
}

/// Keywords whose values may contain `$data`/`$lookup` references.
/// When these resolve to null the keyword should be dropped entirely
/// (matching Python cfn-lint's `_UNRESOLVED` / `continue` behaviour).
const DATA_KEYWORDS: &[&str] = &[
    "const",
    "enum",
    "pattern",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
];

/// Resolve a single JSON value that may contain `$data` or `$lookup`.
pub(crate) fn resolve_data_value(
    value: &serde_json::Value,
    gathered: &AstNode,
) -> serde_json::Value {
    match value {
        serde_json::Value::Object(map) => {
            // Handle $data
            if let Some(data_ref) = map.get("$data").and_then(|v| v.as_str()) {
                if let Some(target) = follow_pointer(gathered, data_ref) {
                    return ast_to_json(target);
                }
                return serde_json::Value::Null;
            }
            // Handle $lookup
            if let Some(lookup) = map.get("$lookup").and_then(|v| v.as_object()) {
                let key = lookup
                    .get("key")
                    .map(|k| resolve_data_value(k, gathered))
                    .unwrap_or(serde_json::Value::Null);
                if let (Some(key_str), Some(lookup_map)) =
                    (key.as_str(), lookup.get("map").and_then(|m| m.as_object()))
                {
                    if let Some(val) = lookup_map.get(key_str) {
                        return val.clone();
                    }
                }
                return serde_json::Value::Null;
            }
            // Regular object — resolve children, dropping data keywords that resolve to null
            let resolved: serde_json::Map<String, serde_json::Value> = map
                .iter()
                .filter_map(|(k, v)| {
                    let resolved_v = resolve_data_value(v, gathered);
                    if resolved_v.is_null() && DATA_KEYWORDS.contains(&k.as_str()) {
                        // Check if the original value was a $data/$lookup reference
                        if is_data_reference(v) {
                            return None; // Drop unresolved data keyword
                        }
                    }
                    Some((k.clone(), resolved_v))
                })
                .collect();
            serde_json::Value::Object(resolved)
        }
        serde_json::Value::Array(arr) => serde_json::Value::Array(
            arr.iter()
                .map(|v| resolve_data_value(v, gathered))
                .collect(),
        ),
        other => other.clone(),
    }
}

/// Check if a JSON value is (or contains at the top level) a `$data` or `$lookup` reference.
pub(crate) fn is_data_reference(value: &serde_json::Value) -> bool {
    if let Some(map) = value.as_object() {
        map.contains_key("$data") || map.contains_key("$lookup")
    } else {
        false
    }
}

/// Build a JSON Schema object for validating resource properties.
/// Extracts all validation-relevant keywords from the full resource provider
/// schema so that `allOf`, `anyOf`, `oneOf`, `if`/`then`/`else`, etc. are
/// preserved and evaluated by the JSON Schema validator.
pub(crate) fn build_resource_properties_schema(
    full_schema: &serde_json::Value,
) -> serde_json::Value {
    const VALIDATION_KEYWORDS: &[&str] = &[
        "type",
        "properties",
        "required",
        "additionalProperties",
        "patternProperties",
        "dependentRequired",
        "dependentExcluded",
        "requiredXor",
        "requiredOr",
        "uniqueKeys",
        "allOf",
        "anyOf",
        "oneOf",
        "not",
        "if",
        "then",
        "else",
        "prefixItems",
        "contains",
        "maxProperties",
        "minProperties",
        "propertyNames",
        "multipleOf",
        "enumCaseInsensitive",
        "definitions",
        "$defs",
    ];

    let obj = match full_schema.as_object() {
        Some(o) => o,
        None => return serde_json::json!({}),
    };

    let mut schema = serde_json::Map::new();
    for &kw in VALIDATION_KEYWORDS {
        if let Some(v) = obj.get(kw) {
            schema.insert(kw.to_string(), v.clone());
        }
    }

    // Ensure we always validate as an object
    schema
        .entry("type".to_string())
        .or_insert_with(|| serde_json::json!("object"));

    serde_json::Value::Object(schema)
}
