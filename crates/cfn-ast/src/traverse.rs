use crate::node::*;

/// Walk the AST tree, calling `visitor` for each node with its path.
pub fn walk<F>(node: &AstNode, path: &[String], visitor: &mut F)
where
    F: FnMut(&AstNode, &[String]) -> bool,
{
    // Convert the caller-supplied prefix to an owned accumulator once, then
    // push/pop per level instead of cloning the whole path at every recursion
    // step (which was O(depth^2) in allocations).
    let mut path = path.to_vec();
    walk_inner(node, &mut path, visitor);
}

fn walk_inner<F>(node: &AstNode, path: &mut Vec<String>, visitor: &mut F)
where
    F: FnMut(&AstNode, &[String]) -> bool,
{
    if !visitor(node, path.as_slice()) {
        return;
    }
    match node {
        AstNode::Object(obj) => {
            for entry in &obj.entries {
                path.push(entry.key.clone());
                walk_inner(&entry.value, path, visitor);
                path.pop();
            }
        }
        AstNode::Array(arr) => {
            for (i, elem) in arr.elements.iter().enumerate() {
                path.push(i.to_string());
                walk_inner(elem, path, visitor);
                path.pop();
            }
        }
        AstNode::Function(func) => {
            walk_inner(&func.args, path, visitor);
        }
        _ => {}
    }
}

/// Find the deepest AstNode at a given cursor position (span-based).
pub fn node_at_position(root: &AstNode, line: u32, col: u32) -> Option<(&AstNode, Vec<String>)> {
    let mut best: Option<(&AstNode, Vec<String>)> = None;
    fn search<'a>(
        node: &'a AstNode,
        path: &mut Vec<String>,
        line: u32,
        col: u32,
        best: &mut Option<(&'a AstNode, Vec<String>)>,
    ) {
        if !span_contains(node.span(), line, col) {
            return;
        }
        // Clone only at the capture point, not at every recursion level.
        *best = Some((node, path.clone()));
        match node {
            AstNode::Object(obj) => {
                for entry in &obj.entries {
                    path.push(entry.key.clone());
                    search(&entry.value, path, line, col, best);
                    path.pop();
                }
            }
            AstNode::Array(arr) => {
                for (i, elem) in arr.elements.iter().enumerate() {
                    path.push(i.to_string());
                    search(elem, path, line, col, best);
                    path.pop();
                }
            }
            AstNode::Function(func) => search(&func.args, path, line, col, best),
            _ => {}
        }
    }
    let mut path = Vec::new();
    search(root, &mut path, line, col, &mut best);
    best
}

/// Find the Function node at a cursor position.
pub fn function_at_position(root: &AstNode, line: u32, col: u32) -> Option<&FunctionNode> {
    fn search(node: &AstNode, line: u32, col: u32) -> Option<&FunctionNode> {
        if !span_contains(node.span(), line, col) {
            return None;
        }
        match node {
            AstNode::Function(func) => search(&func.args, line, col).or(Some(func)),
            AstNode::Object(obj) => obj.values().find_map(|v| search(v, line, col)),
            AstNode::Array(arr) => arr.elements.iter().find_map(|e| search(e, line, col)),
            _ => None,
        }
    }
    search(root, line, col)
}

/// Find the deepest Object context for completion using indentation.
///
/// In YAML, when the cursor is between properties (e.g., on a blank line
/// or at the start of a new key), span-based lookup resolves too high
/// because the previous sibling's span has already ended.
///
/// This function walks the object tree and uses line ordering + column
/// indentation to determine which object the cursor is logically inside.
pub fn object_context_at_position(
    root: &AstNode,
    line: u32,
    col: u32,
) -> Option<(&AstNode, Vec<String>)> {
    let mut best: Option<(&AstNode, Vec<String>)> = None;

    fn search_obj<'a>(
        obj: &'a ObjectNode,
        path: &[String],
        line: u32,
        col: u32,
        best: &mut Option<(&'a AstNode, Vec<String>)>,
    ) {
        let entries: Vec<(&str, &AstNode)> = obj.iter().collect();

        for (i, (key, value)) in entries.iter().enumerate() {
            let value_start_line = value.span().start.line;
            let next_start_line = entries
                .get(i + 1)
                .map(|(_, v)| v.span().start.line)
                .unwrap_or(obj.span.end.line + 1);

            if line >= value_start_line && line < next_start_line {
                let mut child_path = path.to_vec();
                child_path.push((*key).to_string());

                if let AstNode::Object(child_obj) = value {
                    // Object span starts at first key — use that for indent check
                    let child_key_col = child_obj.span.start.column;

                    if col >= child_key_col {
                        *best = Some((*value, child_path.clone()));
                        search_obj(child_obj, &child_path, line, col, best);
                    }
                    // else: cursor is at parent indent level — don't descend,
                    // let the parent object remain as best
                } else {
                    // Non-object value — cursor is in this entry's range
                    // but we stay at the parent level
                }
                return;
            }
        }
    }

    fn search<'a>(
        node: &'a AstNode,
        path: &[String],
        line: u32,
        col: u32,
        best: &mut Option<(&'a AstNode, Vec<String>)>,
    ) {
        if let AstNode::Object(obj) = node {
            if span_contains(node.span(), line, col) || line <= obj.span.end.line + 1 {
                *best = Some((node, path.to_vec()));
                search_obj(obj, path, line, col, best);
            }
        }
    }

    search(root, &[], line, col, &mut best);
    best
}

/// Collect all references to a given name.
pub fn find_references(root: &AstNode, name: &str) -> Vec<Span> {
    let mut spans = Vec::new();
    walk(root, &[], &mut |node, _path| {
        if let AstNode::Function(func) = node {
            match func.name.as_str() {
                "Ref" => {
                    if func.args.as_str() == Some(name) {
                        spans.push(func.span);
                    }
                }
                "Fn::GetAtt" => {
                    let target = match func.args.as_ref() {
                        AstNode::Array(arr) => arr.elements.first().and_then(|e| e.as_str()),
                        AstNode::String(s) => s.value.split('.').next(),
                        _ => None,
                    };
                    if target == Some(name) {
                        spans.push(func.span);
                    }
                }
                "Condition" => {
                    if func.args.as_str() == Some(name) {
                        spans.push(func.span);
                    }
                }
                "Fn::FindInMap" => {
                    if let Some(arr) = func.args.as_array() {
                        if arr.elements.first().and_then(|e| e.as_str()) == Some(name) {
                            spans.push(func.span);
                        }
                    }
                }
                "Fn::Sub" => {
                    let template_str = match func.args.as_ref() {
                        AstNode::String(s) => Some(&s.value),
                        AstNode::Array(arr) => arr.elements.first().and_then(|e| {
                            if let AstNode::String(s) = e {
                                Some(&s.value)
                            } else {
                                None
                            }
                        }),
                        _ => None,
                    };
                    if let Some(s) = template_str {
                        let pattern = format!("${{{}}}", name);
                        if s.contains(&pattern) {
                            spans.push(func.span);
                        }
                    }
                }
                _ => {}
            }
        }
        true
    });
    spans
}

fn span_contains(span: Span, line: u32, col: u32) -> bool {
    if span.start.line == 0 && span.start.column == 0 && span.end.line == 0 && span.end.column == 0
    {
        return false;
    }
    let after_start =
        line > span.start.line || (line == span.start.line && col >= span.start.column);
    let before_end = line < span.end.line || (line == span.end.line && col <= span.end.column);
    after_start && before_end
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser::parse_yaml;

    fn collect_paths(root: &AstNode, prefix: &[String]) -> Vec<Vec<String>> {
        let mut paths: Vec<Vec<String>> = Vec::new();
        walk(root, prefix, &mut |_node, path| {
            paths.push(path.to_vec());
            true
        });
        paths
    }

    #[test]
    fn test_walk_collects_nested_paths() {
        let yaml = "Resources:\n  MyBucket:\n    Type: AWS::S3::Bucket\n";
        let root = parse_yaml(yaml).unwrap();
        let paths = collect_paths(&root, &[]);
        // Root is visited with an empty path.
        assert!(paths.contains(&Vec::<String>::new()));
        // The deep, correctly-ordered path to the Type value is present.
        assert!(
            paths.contains(&vec![
                "Resources".to_string(),
                "MyBucket".to_string(),
                "Type".to_string(),
            ]),
            "missing nested path, got: {paths:?}"
        );
    }

    #[test]
    fn test_walk_pops_path_between_siblings() {
        // Sibling keys must not leak path segments into each other — this is
        // what the push/pop accumulator (replacing per-level cloning) must
        // preserve.
        let yaml = "A:\n  x: 1\nB:\n  y: 2\n";
        let root = parse_yaml(yaml).unwrap();
        let paths = collect_paths(&root, &[]);
        assert!(paths.contains(&vec!["A".to_string(), "x".to_string()]));
        assert!(paths.contains(&vec!["B".to_string(), "y".to_string()]));
        // No cross-contamination.
        assert!(!paths
            .iter()
            .any(|p| p == &vec!["A".to_string(), "B".to_string()]));
        assert!(!paths
            .iter()
            .any(|p| p == &vec!["A".to_string(), "x".to_string(), "y".to_string()]));
    }

    #[test]
    fn test_walk_respects_caller_prefix() {
        let yaml = "x: 1\n";
        let root = parse_yaml(yaml).unwrap();
        let paths = collect_paths(&root, &["root".to_string()]);
        assert!(paths.contains(&vec!["root".to_string()]));
        assert!(paths.contains(&vec!["root".to_string(), "x".to_string()]));
    }

    #[test]
    fn test_node_at_position_builds_correct_path() {
        let yaml = "Resources:\n  MyBucket:\n    Type: AWS::S3::Bucket\n";
        let root = parse_yaml(yaml).unwrap();
        // Line index 2 (0-based) is "    Type: AWS::S3::Bucket"; column 14 sits
        // inside the value.
        let found = node_at_position(&root, 2, 14);
        let (_node, path) = found.expect("expected a node at the Type value position");
        assert!(
            path.starts_with(&["Resources".to_string(), "MyBucket".to_string()]),
            "unexpected path: {path:?}"
        );
    }
}
