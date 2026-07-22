use crate::ast::{ArrayNode, AstNode, FunctionNode, ObjectEntry, ObjectNode};
use crate::resolver::Resolver;

pub(crate) fn expand_fn_if_branches(
    node: &AstNode,
    base_path: Vec<String>,
) -> Vec<(&AstNode, Vec<String>)> {
    if let Some(func) = node.as_function() {
        if func.name == "Fn::If" {
            if let Some(arr) = func.args.as_array() {
                if arr.elements.len() == 3 {
                    let mut branches = Vec::new();
                    for idx in [1usize, 2] {
                        if !is_ref_no_value(&arr.elements[idx]) {
                            branches.extend(expand_fn_if_branches(
                                &arr.elements[idx],
                                base_path.clone(),
                            ));
                        }
                    }
                    if !branches.is_empty() {
                        return branches;
                    }
                }
            }
        }
    }
    vec![(node, base_path)]
}

pub(crate) fn is_ref_no_value(node: &AstNode) -> bool {
    matches!(node, AstNode::Function(f) if f.name == "Ref" && f.args.as_str() == Some("AWS::NoValue"))
}

pub(crate) fn fn_if_non_novalue_branch(node: &AstNode) -> Option<&AstNode> {
    if let AstNode::Function(f) = node {
        if f.name == "Fn::If" {
            if let Some(arr) = f.args.as_array() {
                if arr.elements.len() == 3 {
                    let true_nv = is_ref_no_value(&arr.elements[1]);
                    let false_nv = is_ref_no_value(&arr.elements[2]);
                    if true_nv && !false_nv {
                        return Some(&arr.elements[2]);
                    }
                    if false_nv && !true_nv {
                        return Some(&arr.elements[1]);
                    }
                }
            }
        }
    }
    None
}

pub(crate) fn is_fn_if_with_novalue(node: &AstNode) -> bool {
    fn_if_non_novalue_branch(node).is_some()
}

pub fn resolve_functions(node: &AstNode, resolver: &Resolver) -> AstNode {
    match node {
        AstNode::Function(func) => {
            let resolved_args = resolve_functions(&func.args, resolver);
            let func_with_resolved_args = AstNode::Function(FunctionNode {
                name: func.name.clone(),
                args: Box::new(resolved_args),
                span: func.span,
            });
            match resolver.resolve(&func_with_resolved_args) {
                Some(resolved) => resolved,
                None => {
                    if let Some(branch) = fn_if_non_novalue_branch(&func_with_resolved_args) {
                        resolve_functions(branch, resolver)
                    } else {
                        func_with_resolved_args
                    }
                }
            }
        }
        AstNode::Object(obj) => {
            let entries: Vec<ObjectEntry> = obj
                .entries
                .iter()
                .filter(|e| !is_ref_no_value(&e.value) && !is_fn_if_with_novalue(&e.value))
                .map(|e| ObjectEntry {
                    key_node: e.key_node.clone(),
                    key: e.key.clone(),
                    value: resolve_functions(&e.value, resolver),
                    key_span: e.key_span,
                })
                .filter(|e| !matches!(e.value, AstNode::Null(_)))
                .collect();
            AstNode::Object(ObjectNode {
                entries,
                span: obj.span,
            })
        }
        AstNode::Array(arr) => {
            let elements = arr
                .elements
                .iter()
                .map(|e| resolve_functions(e, resolver))
                .collect();
            AstNode::Array(ArrayNode {
                elements,
                span: arr.span,
            })
        }
        _ => node.clone(),
    }
}

/// Extract ignored rule IDs from Metadata/cfn-lint/config/ignore_checks.
pub fn get_ignored_rules(node: &AstNode) -> Vec<String> {
    node.get("Metadata")
        .and_then(|m| m.get("cfn-lint"))
        .and_then(|c| c.get("config"))
        .and_then(|c| c.get("ignore_checks"))
        .and_then(|a| a.as_array())
        .map(|arr| {
            arr.elements
                .iter()
                .filter_map(|e| e.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default()
}
