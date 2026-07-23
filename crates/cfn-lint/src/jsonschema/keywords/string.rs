use super::super::{ValidationError, Validator};
use super::helpers::{compile_pattern, err};
use crate::ast::AstNode;

pub fn validate_min_length(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (AstNode::String(s), Some(min)) = (node, constraint.as_u64()) {
        // JSON Schema counts length in Unicode code points, not UTF-8 bytes.
        let len = s.value.chars().count();
        if len < min as usize {
            return vec![err(
                "minLength",
                format!("expected minimum length: {}, found: {}", min, len),
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
        // JSON Schema counts length in Unicode code points, not UTF-8 bytes.
        let len = s.value.chars().count();
        if len > max as usize {
            return vec![err(
                "maxLength",
                format!("expected maximum length: {}, found: {}", max, len),
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
        // Compiled regexes are cached by pattern so each distinct pattern is
        // compiled at most once instead of on every invocation. The cache
        // constructor (compile_pattern) applies the fancy_regex backtrack
        // limit for the fallback engine, preserving the ReDoS protection.
        let matched = match compile_pattern(pat) {
            Some(re) => re.is_match(&s.value),
            None => return vec![],
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

#[cfg(test)]
mod tests {
    use super::*;

    fn run_with_timeout<F: FnOnce() + Send + 'static>(secs: u64, f: F) {
        use std::sync::mpsc::{channel, RecvTimeoutError};
        use std::time::Duration;
        let (tx, rx) = channel();
        let handle = std::thread::spawn(move || {
            f();
            let _ = tx.send(());
        });
        match rx.recv_timeout(Duration::from_secs(secs)) {
            Ok(()) => handle.join().unwrap(),
            Err(RecvTimeoutError::Timeout) => {
                panic!("did not finish within {secs}s — regex backtrack limit likely regressed")
            }
            Err(RecvTimeoutError::Disconnected) => handle.join().unwrap(),
        }
    }

    fn str_node(s: &str) -> AstNode {
        AstNode::String(crate::ast::StringNode {
            value: s.to_string(),
            span: crate::ast::Span::default(),
        })
    }

    #[test]
    fn test_catastrophic_backtracking_pattern_terminates() {
        run_with_timeout(10, || {
            // Lookahead is unsupported by the linear `regex` crate, so this pattern
            // falls back to fancy_regex. The nested quantifier is a classic ReDoS
            // trigger; on this non-matching input it would backtrack exponentially
            // without the bounded backtrack limit.
            let v = Validator::new(serde_json::json!({}));
            let constraint = serde_json::json!("^(?=(a+)+$)");
            let value = format!("{}!", "a".repeat(50));
            let node = str_node(&value);
            // The key property is that this returns at all (quickly); the value does
            // not match, so a pattern error is the expected result.
            let errs = validate_pattern(&v, &node, &constraint, &serde_json::json!({}), &[]);
            assert!(errs.iter().all(|e| e.keyword == "pattern"));
        });
    }

    #[test]
    fn test_normal_pattern_still_matches() {
        let v = Validator::new(serde_json::json!({}));
        let constraint = serde_json::json!("^[a-z]+$");
        assert!(validate_pattern(
            &v,
            &str_node("abc"),
            &constraint,
            &serde_json::json!({}),
            &[]
        )
        .is_empty());
        assert!(!validate_pattern(
            &v,
            &str_node("ABC"),
            &constraint,
            &serde_json::json!({}),
            &[]
        )
        .is_empty());
    }
}
