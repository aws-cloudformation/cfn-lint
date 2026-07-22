use super::super::ValidationError;
use crate::ast::AstNode;
use regex::Regex;
use std::collections::HashMap;
use std::sync::{Arc, LazyLock, Mutex};

/// A compiled regular expression, using the standard `regex` engine when
/// possible and falling back to `fancy_regex` for patterns that require
/// features (such as look-around or backreferences) the standard engine lacks.
pub enum CachedRegex {
    Standard(Regex),
    Fancy(fancy_regex::Regex),
}

impl CachedRegex {
    pub fn is_match(&self, text: &str) -> bool {
        match self {
            CachedRegex::Standard(re) => re.is_match(text),
            CachedRegex::Fancy(re) => re.is_match(text).unwrap_or(false),
        }
    }
}

static PATTERN_CACHE: LazyLock<Mutex<HashMap<String, Option<Arc<CachedRegex>>>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

/// Compile a `pattern` keyword regex with caching. Tries the standard regex
/// engine first, then `fancy_regex`. Returns `None` when neither engine can
/// compile the pattern. Results (including compile failures) are cached keyed
/// by the pattern string, so each distinct pattern is compiled at most once
/// rather than on every validation.
pub fn compile_pattern(pattern: &str) -> Option<Arc<CachedRegex>> {
    if let Some(entry) = PATTERN_CACHE.lock().unwrap().get(pattern) {
        return entry.clone();
    }
    let compiled = Regex::new(pattern)
        .ok()
        .map(|re| Arc::new(CachedRegex::Standard(re)))
        .or_else(|| {
            // Use the backtrack-limited constructor so the fancy_regex fallback
            // keeps the ReDoS protection (FANCY_REGEX_BACKTRACK_LIMIT); untrusted
            // schema patterns must not enable catastrophic backtracking.
            build_fancy_regex(pattern).map(|re| Arc::new(CachedRegex::Fancy(re)))
        });
    PATTERN_CACHE
        .lock()
        .unwrap()
        .insert(pattern.to_string(), compiled.clone());
    compiled
}

static GETATT_REGEX_CACHE: LazyLock<Mutex<HashMap<String, Option<Arc<Regex>>>>> =
    LazyLock::new(|| Mutex::new(HashMap::new()));

/// Compile a standard-engine regex with caching (no `fancy_regex` fallback).
/// Used to match Fn::GetAtt attribute patterns, where the standard engine's
/// semantics must be preserved. Returns `None` for patterns the standard
/// engine cannot compile. Compiled results are cached by pattern so the same
/// resource-type attribute pattern is compiled at most once.
pub fn compile_getatt_regex(pattern: &str) -> Option<Arc<Regex>> {
    if let Some(entry) = GETATT_REGEX_CACHE.lock().unwrap().get(pattern) {
        return entry.clone();
    }
    let compiled = Regex::new(pattern).ok().map(Arc::new);
    GETATT_REGEX_CACHE
        .lock()
        .unwrap()
        .insert(pattern.to_string(), compiled.clone());
    compiled
}

/// Backtrack limit for the `fancy_regex` fallback engine.
///
/// Schema `pattern` / `patternProperties` values are untrusted input. The
/// `fancy_regex` engine (used only when the linear-time `regex` crate rejects a
/// pattern) can exhibit catastrophic backtracking — a ReDoS vector. Capping the
/// backtracking steps per match attempt bounds the work: once the limit is hit,
/// `is_match` returns `Err`, which callers treat as "no match".
pub const FANCY_REGEX_BACKTRACK_LIMIT: usize = 1_000_000;

/// Build a `fancy_regex::Regex` with a bounded backtrack limit to prevent ReDoS
/// from adversarial schema patterns. Returns `None` if the pattern is invalid.
pub fn build_fancy_regex(pattern: &str) -> Option<fancy_regex::Regex> {
    fancy_regex::RegexBuilder::new(pattern)
        .backtrack_limit(FANCY_REGEX_BACKTRACK_LIMIT)
        .build()
        .ok()
}

/// Format a JSON value the way Python's `repr()` renders it, matching the
/// message wording of Python cfn-lint: strings are single-quoted, booleans are
/// capitalized (`True`/`False`), `null` becomes `None`, and arrays/objects use
/// Python's `[...]` / `{'key': value}` syntax. Used so parity messages such as
/// `'REPLICA' was expected` and `{'Nested': 'object'} is not of type ...`
/// match Python byte-for-byte.
pub fn python_repr(value: &serde_json::Value) -> String {
    match value {
        serde_json::Value::Null => "None".to_string(),
        serde_json::Value::Bool(true) => "True".to_string(),
        serde_json::Value::Bool(false) => "False".to_string(),
        serde_json::Value::Number(n) => n.to_string(),
        serde_json::Value::String(s) => format!("'{}'", s),
        serde_json::Value::Array(arr) => {
            let items: Vec<String> = arr.iter().map(python_repr).collect();
            format!("[{}]", items.join(", "))
        }
        serde_json::Value::Object(map) => {
            let items: Vec<String> = map
                .iter()
                .map(|(k, v)| format!("'{}': {}", k, python_repr(v)))
                .collect();
            format!("{{{}}}", items.join(", "))
        }
    }
}

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
        (AstNode::Number(n), serde_json::Value::Number(v)) => {
            // const/enum require exact equality. An epsilon comparison is wrong
            // here: large integers (>1e15) whose ULP exceeds EPSILON compare
            // unequal, and distinct near-zero values compare equal.
            #[allow(clippy::float_cmp)]
            v.as_f64().is_some_and(|f| n.value == f)
        }
        (AstNode::Bool(b), serde_json::Value::Bool(v)) => b.value == *v,
        (AstNode::Null(_), serde_json::Value::Null) => true,
        (AstNode::Object(o), serde_json::Value::Object(m)) => {
            o.len() == m.len()
                && o.iter()
                    .all(|(k, v)| m.get(k).is_some_and(|mv| ast_matches_json(v, mv)))
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
            let items: Vec<serde_json::Value> =
                arr.elements.iter().filter_map(ast_to_json_value).collect();
            serde_json::Value::Array(items)
        }
        AstNode::Function(func) => {
            let mut map = serde_json::Map::new();
            map.insert(func.name.clone(), ast_to_json_value(&func.args)?);
            serde_json::Value::Object(map)
        }
    })
}
