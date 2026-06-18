use crate::node::*;

/// Walk the AST tree, calling `visitor` for each node with its path.
pub fn walk<F>(node: &AstNode, path: &[String], visitor: &mut F)
where
    F: FnMut(&AstNode, &[String]) -> bool,
{
    if !visitor(node, path) {
        return;
    }
    match node {
        AstNode::Object(obj) => {
            for entry in &obj.entries {
                let mut child_path = path.to_vec();
                child_path.push(entry.key.clone());
                walk(&entry.value, &child_path, visitor);
            }
        }
        AstNode::Array(arr) => {
            for (i, elem) in arr.elements.iter().enumerate() {
                let mut child_path = path.to_vec();
                child_path.push(i.to_string());
                walk(elem, &child_path, visitor);
            }
        }
        AstNode::Function(func) => {
            walk(&func.args, path, visitor);
        }
        _ => {}
    }
}

/// Find the deepest AstNode at a given cursor position (span-based).
pub fn node_at_position(root: &AstNode, line: u32, col: u32) -> Option<(&AstNode, Vec<String>)> {
    let mut best: Option<(&AstNode, Vec<String>)> = None;
    fn search<'a>(
        node: &'a AstNode,
        path: &[String],
        line: u32,
        col: u32,
        best: &mut Option<(&'a AstNode, Vec<String>)>,
    ) {
        if !span_contains(node.span(), line, col) {
            return;
        }
        *best = Some((node, path.to_vec()));
        match node {
            AstNode::Object(obj) => {
                for entry in &obj.entries {
                    let mut p = path.to_vec();
                    p.push(entry.key.clone());
                    search(&entry.value, &p, line, col, best);
                }
            }
            AstNode::Array(arr) => {
                for (i, elem) in arr.elements.iter().enumerate() {
                    let mut p = path.to_vec();
                    p.push(i.to_string());
                    search(elem, &p, line, col, best);
                }
            }
            AstNode::Function(func) => search(&func.args, path, line, col, best),
            _ => {}
        }
    }
    search(root, &[], line, col, &mut best);
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
