//! Helpers for keyword rules, mirroring Python's `cfnlint.rules.helpers`.

use std::collections::VecDeque;

use crate::ast::AstNode;
use crate::context::Context;

/// Walk a path through an AstNode, branching through Fn::If conditions.
///
/// Yields `(value, context)` pairs where the context has evolved condition
/// state for each Fn::If branch taken. This is how keyword rules become
/// condition-aware.
///
/// Mirrors Python's `get_value_from_path`.
pub fn get_value_from_path<'a>(
    ctx: &Context,
    instance: Option<&'a AstNode>,
    path: &mut VecDeque<String>,
) -> Vec<(Option<&'a AstNode>, Context)> {
    let instance = match instance {
        Some(i) => i,
        None => return vec![(None, ctx.clone())],
    };

    // Check for intrinsic functions
    if let Some(func) = instance.as_function() {
        if func.name == "Fn::If" {
            return get_value_fn_if(ctx, instance, path);
        }
        if func.name == "Ref" {
            if let Some("AWS::NoValue") = func.args.as_str() {
                return vec![(None, ctx.clone())];
            }
        }
        // Other functions: if path is empty, yield the function as-is
        if path.is_empty() {
            return vec![(Some(instance), ctx.clone())];
        }
        // Can't descend into an unresolvable function
        return vec![];
    }

    // No more path to walk — yield current value
    if path.is_empty() {
        return vec![(Some(instance), ctx.clone())];
    }

    let key = path.pop_front().unwrap();

    // Wildcard: iterate array elements
    if key == "*" {
        if let Some(arr) = instance.as_array() {
            let mut results = Vec::new();
            for elem in &arr.elements {
                results.extend(get_value_from_path(ctx, Some(elem), &mut path.clone()));
            }
            return results;
        }
        return vec![(None, ctx.clone())];
    }

    // Dict key lookup
    match instance.get(&key) {
        Some(child) => get_value_from_path(ctx, Some(child), path),
        None => vec![(None, ctx.clone())],
    }
}

/// Handle Fn::If: branch into true and false with evolved condition state.
fn get_value_fn_if<'a>(
    ctx: &Context,
    instance: &'a AstNode,
    path: &mut VecDeque<String>,
) -> Vec<(Option<&'a AstNode>, Context)> {
    let func = match instance.as_function() {
        Some(f) => f,
        None => return vec![],
    };
    let args = match func.args.as_array() {
        Some(a) if a.elements.len() == 3 => a,
        _ => return vec![],
    };
    let condition = match args.elements[0].as_str() {
        Some(s) => s.to_string(),
        None => return vec![],
    };

    let mut results = Vec::new();

    // True branch
    if ctx.condition_state.get(&condition) != Some(&false) {
        let mut true_ctx = ctx.clone();
        true_ctx.condition_state.insert(condition.clone(), true);
        results.extend(get_value_from_path(
            &true_ctx,
            Some(&args.elements[1]),
            &mut path.clone(),
        ));
    }

    // False branch
    if ctx.condition_state.get(&condition) != Some(&true) {
        let mut false_ctx = ctx.clone();
        false_ctx.condition_state.insert(condition, false);
        results.extend(get_value_from_path(
            &false_ctx,
            Some(&args.elements[2]),
            &mut path.clone(),
        ));
    }

    results
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;
    use std::sync::Arc;

    fn make_ctx(yaml: &[u8]) -> (AstNode, Context) {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Arc::new(Template::from_ast(&ast).unwrap());
        let ctx = Context::new(tmpl);
        (ast, ctx)
    }

    #[test]
    fn test_simple_path() {
        let (ast, ctx) = make_ctx(b"a:\n  b:\n    c: hello\n");
        let mut path = VecDeque::from(["a".into(), "b".into(), "c".into()]);
        let results = get_value_from_path(&ctx, Some(&ast), &mut path);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].0.unwrap().as_str(), Some("hello"));
    }

    #[test]
    fn test_missing_key() {
        let (ast, ctx) = make_ctx(b"a:\n  b: 1\n");
        let mut path = VecDeque::from(["a".into(), "missing".into()]);
        let results = get_value_from_path(&ctx, Some(&ast), &mut path);
        assert_eq!(results.len(), 1);
        assert!(results[0].0.is_none());
    }

    #[test]
    fn test_fn_if_branches() {
        let (ast, ctx) =
            make_ctx(b"val:\n  Fn::If:\n    - IsProd\n    - prod-value\n    - dev-value\n");
        let mut path = VecDeque::from(["val".into()]);
        let results = get_value_from_path(&ctx, Some(&ast), &mut path);
        assert_eq!(results.len(), 2);
        let values: Vec<_> = results
            .iter()
            .filter_map(|(v, _)| v.and_then(|n| n.as_str()))
            .collect();
        assert!(values.contains(&"prod-value"));
        assert!(values.contains(&"dev-value"));
        // Check condition state is pinned
        assert_eq!(results[0].1.condition_state.get("IsProd"), Some(&true));
        assert_eq!(results[1].1.condition_state.get("IsProd"), Some(&false));
    }

    #[test]
    fn test_fn_if_with_pinned_condition() {
        let (ast, mut ctx) =
            make_ctx(b"val:\n  Fn::If:\n    - IsProd\n    - prod-value\n    - dev-value\n");
        ctx.condition_state.insert("IsProd".into(), true);
        let mut path = VecDeque::from(["val".into()]);
        let results = get_value_from_path(&ctx, Some(&ast), &mut path);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].0.unwrap().as_str(), Some("prod-value"));
    }

    #[test]
    fn test_ref_aws_novalue() {
        let (ast, ctx) = make_ctx(b"val:\n  Ref: 'AWS::NoValue'\n");
        let mut path = VecDeque::from(["val".into()]);
        let results = get_value_from_path(&ctx, Some(&ast), &mut path);
        assert_eq!(results.len(), 1);
        assert!(results[0].0.is_none());
    }

    #[test]
    fn test_wildcard_array() {
        let (ast, ctx) = make_ctx(b"items:\n  - name: a\n  - name: b\n");
        let mut path = VecDeque::from(["items".into(), "*".into(), "name".into()]);
        let results = get_value_from_path(&ctx, Some(&ast), &mut path);
        assert_eq!(results.len(), 2);
        let values: Vec<_> = results
            .iter()
            .filter_map(|(v, _)| v.and_then(|n| n.as_str()))
            .collect();
        assert!(values.contains(&"a"));
        assert!(values.contains(&"b"));
    }

    #[test]
    fn test_empty_path_returns_instance() {
        let (ast, ctx) = make_ctx(b"hello: world\n");
        let mut path = VecDeque::new();
        let results = get_value_from_path(&ctx, Some(&ast), &mut path);
        assert_eq!(results.len(), 1);
        assert!(results[0].0.is_some());
    }
}
