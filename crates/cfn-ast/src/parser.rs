use crate::node::*;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ParseError {
    #[error("YAML parse error: {0}")]
    Yaml(String),
    #[error("JSON parse error: {0}")]
    Json(#[from] serde_json::Error),
}

const CFN_FUNCTIONS: &[&str] = &[
    "Ref",
    "Fn::Base64",
    "Fn::Cidr",
    "Fn::Equals",
    "Fn::And",
    "Fn::Or",
    "Fn::Not",
    "Fn::FindInMap",
    "Fn::GetAtt",
    "Fn::GetAZs",
    "Fn::GetStackOutput",
    "Fn::If",
    "Fn::ImportValue",
    "Fn::Join",
    "Fn::Length",
    "Fn::Select",
    "Fn::Split",
    "Fn::Sub",
    "Fn::ToJsonString",
    "Fn::Transform",
    "Fn::ForEach",
    "Condition",
];

fn resolve_yaml11_bool(value: &str) -> Option<bool> {
    match value {
        "yes" | "Yes" | "YES" | "on" | "On" | "ON" => Some(true),
        "no" | "No" | "NO" | "off" | "Off" | "OFF" => Some(false),
        _ => None,
    }
}

/// Byte offset → line/column converter for JSON spans.
struct LineIndex {
    line_starts: Vec<usize>,
}

impl LineIndex {
    fn new(text: &str) -> Self {
        let mut starts = vec![0];
        for (i, b) in text.bytes().enumerate() {
            if b == b'\n' {
                starts.push(i + 1);
            }
        }
        Self { line_starts: starts }
    }

    fn position(&self, offset: usize) -> Position {
        let line = self.line_starts.partition_point(|&s| s <= offset).saturating_sub(1);
        let col = offset - self.line_starts[line];
        Position {
            line: line as u32,
            column: col as u32,
        }
    }

    fn span(&self, range: std::ops::Range<usize>) -> Span {
        Span {
            start: self.position(range.start),
            end: self.position(range.end),
        }
    }
}

// ── YAML parsing via yaml-rust2 ──

use crate::yaml::parser::{Event, MarkedEventReceiver, Parser, Tag};
use crate::yaml::scanner::{Marker, TScalarStyle};

fn marker_to_pos(m: Marker) -> Position {
    Position {
        line: m.line().saturating_sub(1) as u32,  // yaml-rust2 lines are 1-based
        column: m.col() as u32,                    // yaml-rust2 columns are 0-based
    }
}

const YAML_TAG_MAP: &[(&str, &str)] = &[
    ("!Ref", "Ref"),
    ("!Sub", "Fn::Sub"),
    ("!GetAtt", "Fn::GetAtt"),
    ("!If", "Fn::If"),
    ("!Join", "Fn::Join"),
    ("!Select", "Fn::Select"),
    ("!Split", "Fn::Split"),
    ("!FindInMap", "Fn::FindInMap"),
    ("!Base64", "Fn::Base64"),
    ("!Cidr", "Fn::Cidr"),
    ("!GetAZs", "Fn::GetAZs"),
    ("!ImportValue", "Fn::ImportValue"),
    ("!Condition", "Condition"),
    ("!And", "Fn::And"),
    ("!Or", "Fn::Or"),
    ("!Not", "Fn::Not"),
    ("!Equals", "Fn::Equals"),
    ("!Transform", "Fn::Transform"),
    ("!ToJsonString", "Fn::ToJsonString"),
    ("!Length", "Fn::Length"),
    ("!ForEach", "Fn::ForEach"),
    ("!GetStackOutput", "Fn::GetStackOutput"),
];

fn resolve_tag(tag: &Tag) -> Option<&'static str> {
    let tag_str = format!("!{}", tag.suffix);
    YAML_TAG_MAP.iter().find(|(k, _)| *k == tag_str).map(|(_, v)| *v)
}

/// Pending key info while parsing a YAML mapping.
struct PendingKey {
    key_node: AstNode,
    key: String,
    key_span: Span,
}

/// Custom YAML loader that tracks positions via MarkedEventReceiver.
struct CfnYamlLoader {
    doc_stack: Vec<(AstNode, Option<String>)>,
    pending_key_stack: Vec<Option<PendingKey>>,
    mark_stack: Vec<Marker>,
    result: Option<AstNode>,
}

impl CfnYamlLoader {
    fn new() -> Self {
        Self {
            doc_stack: Vec::new(),
            pending_key_stack: Vec::new(),
            mark_stack: Vec::new(),
            result: None,
        }
    }

    fn insert_node(&mut self, node: AstNode, mark: Marker) {
        if self.doc_stack.is_empty() {
            self.doc_stack.push((node, None));
            return;
        }

        let parent = self.doc_stack.last_mut().unwrap();
        match &mut parent.0 {
            AstNode::Array(arr) => arr.elements.push(node),
            AstNode::Object(obj) => {
                let pending = self.pending_key_stack.last_mut().unwrap();
                if pending.is_none() {
                    // This node is a key — record it
                    let pos = marker_to_pos(mark);
                    let len = match &node {
                        AstNode::String(s) => s.value.len() as u32,
                        _ => 0,
                    };
                    let key_span = Span {
                        start: pos,
                        end: Position { line: pos.line, column: pos.column + len },
                    };
                    let key = match &node {
                        AstNode::String(s) => s.value.clone(),
                        other => format!("{}", other),
                    };
                    *pending = Some(PendingKey { key_node: node, key, key_span });
                } else {
                    // This node is a value — create entry
                    let pk = pending.take().unwrap();
                    obj.entries.push(ObjectEntry {
                        key_node: pk.key_node,
                        key: pk.key,
                        value: node,
                        key_span: pk.key_span,
                    });
                }
            }
            _ => {}
        }
    }
}

impl MarkedEventReceiver for CfnYamlLoader {
    fn on_event(&mut self, ev: Event, mark: Marker) {
        match ev {
            Event::DocumentStart | Event::Nothing | Event::StreamStart | Event::StreamEnd => {}
            Event::DocumentEnd => {
                if let Some((node, _)) = self.doc_stack.pop() {
                    self.result = Some(node);
                }
            }
            Event::SequenceStart(_, tag) => {
                let func_name = tag.as_ref().and_then(resolve_tag).map(String::from);
                self.doc_stack.push((
                    AstNode::Array(ArrayNode {
                        elements: Vec::new(),
                        span: Span {
                            start: marker_to_pos(mark),
                            end: Position::default(),
                        },
                    }),
                    func_name,
                ));
                self.mark_stack.push(mark);
            }
            Event::SequenceEnd => {
                let start_mark = self.mark_stack.pop().unwrap_or(mark);
                let (mut node, func_name) = self.doc_stack.pop().unwrap();
                // Update end position
                if let AstNode::Array(arr) = &mut node {
                    arr.span.end = marker_to_pos(mark);
                }
                // Wrap in function if tagged
                let node = if let Some(name) = func_name {
                    AstNode::Function(FunctionNode {
                        name,
                        args: Box::new(node),
                        span: Span {
                            start: marker_to_pos(start_mark),
                            end: marker_to_pos(mark),
                        },
                    })
                } else {
                    node
                };
                self.insert_node(node, mark);
            }
            Event::MappingStart(_, tag) => {
                let func_name = tag.as_ref().and_then(resolve_tag).map(String::from);
                self.doc_stack.push((
                    AstNode::Object(ObjectNode {
                        entries: Vec::new(),
                        span: Span {
                            start: marker_to_pos(mark),
                            end: Position::default(),
                        },
                    }),
                    func_name,
                ));
                self.pending_key_stack.push(None);
                self.mark_stack.push(mark);
            }
            Event::MappingEnd => {
                let start_mark = self.mark_stack.pop().unwrap_or(mark);
                self.pending_key_stack.pop();
                let (mut node, func_name) = self.doc_stack.pop().unwrap();
                // Update end position
                if let AstNode::Object(obj) = &mut node {
                    obj.span.end = marker_to_pos(mark);
                    // Fix span start to use first key position (more accurate than MappingStart)
                    if let Some(first_entry) = obj.entries.first() {
                        obj.span.start = first_entry.key_span.start;
                    }
                }
                // Check for CFN function (single-key mapping)
                let node = if let AstNode::Object(ref obj) = node {
                    if obj.entries.len() == 1 {
                        let entry = &obj.entries[0];
                        if CFN_FUNCTIONS.contains(&entry.key.as_str()) {
                            AstNode::Function(FunctionNode {
                                name: entry.key.clone(),
                                args: Box::new(entry.value.clone()),
                                span: Span {
                                    start: marker_to_pos(start_mark),
                                    end: marker_to_pos(mark),
                                },
                            })
                        } else {
                            node
                        }
                    } else {
                        node
                    }
                } else {
                    node
                };
                // Wrap in function if tagged
                let node = if let Some(name) = func_name {
                    AstNode::Function(FunctionNode {
                        name,
                        args: Box::new(node),
                        span: Span {
                            start: marker_to_pos(start_mark),
                            end: marker_to_pos(mark),
                        },
                    })
                } else {
                    node
                };
                self.insert_node(node, mark);
            }
            Event::Scalar(value, style, _, tag) => {
                let start = marker_to_pos(mark);
                let span = Span {
                    start,
                    end: Position {
                        line: start.line,
                        column: start.column + value.len() as u32,
                    },
                };

                // Check for tag-based function
                if let Some(func_name) = tag.as_ref().and_then(resolve_tag) {
                    // Extend span backwards to cover the tag (e.g., "!Ref ")
                    let tag_text = tag.as_ref().map(|t| format!("!{} ", t.suffix)).unwrap_or_default();
                    let func_start = marker_to_pos(mark);
                    let func_span = Span {
                        start: Position {
                            line: func_start.line,
                            column: func_start.column.saturating_sub(tag_text.len() as u32),
                        },
                        end: span.end,
                    };
                    let inner = AstNode::String(StringNode {
                        value: value.clone(),
                        span,
                    });
                    let node = AstNode::Function(FunctionNode {
                        name: func_name.to_string(),
                        args: Box::new(inner),
                        span: func_span,
                    });
                    self.insert_node(node, mark);
                    return;
                }

                // Quoted strings stay as strings
                let node = if style != TScalarStyle::Plain {
                    AstNode::String(StringNode { value, span })
                } else if let Some(b) = resolve_yaml11_bool(&value) {
                    AstNode::Bool(BoolNode { value: b, span })
                } else {
                    match value.as_str() {
                        "true" | "True" | "TRUE" => AstNode::Bool(BoolNode { value: true, span }),
                        "false" | "False" | "FALSE" => AstNode::Bool(BoolNode { value: false, span }),
                        "~" | "null" | "Null" | "NULL" | "" => AstNode::Null(NullNode { span }),
                        _ => {
                            if let Ok(n) = value.parse::<f64>() {
                                AstNode::Number(NumberNode { value: n, span })
                            } else {
                                AstNode::String(StringNode { value, span })
                            }
                        }
                    }
                };
                self.insert_node(node, mark);
            }
            Event::Alias(_) => {
                // Not supported yet
            }
        }
    }
}

/// Parse YAML text into an AstNode.
pub fn parse_yaml(input: &str) -> Result<AstNode, ParseError> {
    let mut loader = CfnYamlLoader::new();
    let mut parser = Parser::new(input.chars());
    parser.load(&mut loader, true).map_err(|e| ParseError::Yaml(e.to_string()))?;
    loader.result.ok_or_else(|| ParseError::Yaml("empty document".to_string()))
}

/// Parse YAML text leniently — on error, recover the partial AST built so far.
/// Returns (ast, errors) where errors is empty on success.
pub fn parse_yaml_lenient(input: &str) -> (Option<AstNode>, Vec<String>) {
    let mut loader = CfnYamlLoader::new();
    let mut parser = Parser::new(input.chars());
    let mut errors = Vec::new();

    if let Err(e) = parser.load(&mut loader, true) {
        let error_line = (e.marker().line() as u32).saturating_sub(1);
        let error_col = e.marker().col() as u32;
        errors.push(e.to_string());

        // Recover partial AST: unwind the doc_stack, closing each open node
        // and inserting it into its parent, bottom-up.
        while loader.doc_stack.len() > 1 {
            // Handle any pending key at this level (incomplete key without value)
            if let Some(pending) = loader.pending_key_stack.last_mut() {
                if let Some(pk) = pending.take() {
                    // Key was started but no value — insert with null value
                    if let Some((AstNode::Object(obj), _)) = loader.doc_stack.last_mut() {
                        obj.entries.push(ObjectEntry {
                            key_node: pk.key_node,
                            key: pk.key,
                            value: AstNode::Null(NullNode { span: pk.key_span }),
                            key_span: pk.key_span,
                        });
                    }
                }
            }

            let (mut node, func_name) = loader.doc_stack.pop().unwrap();

            // Pop the pending_key_stack for this mapping level
            if matches!(node, AstNode::Object(_)) {
                loader.pending_key_stack.pop();
            }

            // Update end span to cover up to the error position
            match &mut node {
                AstNode::Object(obj) => {
                    obj.span.end = Position { line: error_line, column: error_col };
                }
                AstNode::Array(arr) => {
                    arr.span.end = Position { line: error_line, column: error_col };
                }
                _ => {}
            }

            // Wrap in function if tagged
            let node = if let Some(name) = func_name {
                let span = node.span();
                AstNode::Function(FunctionNode { name, args: Box::new(node), span })
            } else {
                node
            };

            // Insert into parent
            if let Some(parent) = loader.doc_stack.last_mut() {
                match &mut parent.0 {
                    AstNode::Array(arr) => arr.elements.push(node),
                    AstNode::Object(obj) => {
                        // Check if parent has a pending key waiting for this value
                        let pending = loader.pending_key_stack.last_mut().and_then(|p| p.take());
                        if let Some(pk) = pending {
                            obj.entries.push(ObjectEntry {
                                key_node: pk.key_node,
                                key: pk.key,
                                value: node,
                                key_span: pk.key_span,
                            });
                        }
                    }
                    _ => {}
                }
            }
        }

        // The last item on the stack is the root
        if let Some((node, _)) = loader.doc_stack.pop() {
            loader.result = Some(node);
        }

        // Try to recover content after the error by finding the next valid
        // top-level or sibling key and parsing from there.
        if let Some(ref mut root) = loader.result {
            if let Some(root_obj) = root.as_object_mut() {
                let lines: Vec<&str> = input.lines().collect();
                let err_line = error_line.saturating_sub(1) as usize; // scanner is 1-indexed

                // Find lines after the error that are at the root indentation level (col 0)
                // These are likely top-level keys like "Outputs:", "Parameters:", etc.
                for start_line in err_line..lines.len() {
                    let line = lines[start_line];
                    if !line.starts_with(' ') && !line.starts_with('#') && !line.trim().is_empty() && line.contains(':') {
                        // Found a potential top-level key — try parsing from here
                        let remaining = lines[start_line..].join("\n");
                        if let Ok(partial) = parse_yaml(&remaining) {
                            if let AstNode::Object(partial_obj) = partial {
                                // Merge entries, adjusting line numbers
                                for mut entry in partial_obj.entries {
                                    // Adjust spans
                                    let offset = start_line as u32;
                                    adjust_spans(&mut entry.value, offset);
                                    entry.key_span.start.line += offset;
                                    entry.key_span.end.line += offset;
                                    if let AstNode::String(ref mut s) = entry.key_node {
                                        s.span.start.line += offset;
                                        s.span.end.line += offset;
                                    }
                                    root_obj.entries.push(entry);
                                }
                                root_obj.span.end = Position { line: lines.len() as u32, column: 0 };
                            }
                        }
                        break;
                    }
                }

                // Also check for sibling keys at the same indent as the error
                // (e.g., another resource after a broken one)
                if err_line < lines.len() {
                    let err_indent = lines.get(err_line).map(|l| l.len() - l.trim_start().len()).unwrap_or(0);
                    for start_line in err_line..lines.len() {
                        let line = lines[start_line];
                        let indent = line.len() - line.trim_start().len();
                        if indent <= err_indent && !line.trim().is_empty() && line.contains(':') && indent > 0 {
                            // Found a sibling key — try parsing a sub-document
                            let remaining = lines[start_line..].join("\n");
                            if let Ok(partial) = parse_yaml(&remaining) {
                                if let AstNode::Object(partial_obj) = partial {
                                    // Find the parent in the root to merge into
                                    let offset = start_line as u32;
                                    for mut entry in partial_obj.entries {
                                        adjust_spans(&mut entry.value, offset);
                                        entry.key_span.start.line += offset;
                                        entry.key_span.end.line += offset;
                                        if let AstNode::String(ref mut s) = entry.key_node {
                                            s.span.start.line += offset;
                                            s.span.end.line += offset;
                                        }
                                        // Try to find the right parent section
                                        merge_entry_into_parent(root_obj, entry, indent);
                                    }
                                }
                            }
                            break;
                        }
                    }
                }
            }
        }
    }

    (loader.result, errors)
}

/// Adjust all spans in an AST node by adding a line offset.
fn adjust_spans(node: &mut AstNode, line_offset: u32) {
    match node {
        AstNode::Object(obj) => {
            obj.span.start.line += line_offset;
            obj.span.end.line += line_offset;
            for entry in &mut obj.entries {
                entry.key_span.start.line += line_offset;
                entry.key_span.end.line += line_offset;
                if let AstNode::String(ref mut s) = entry.key_node {
                    s.span.start.line += line_offset;
                    s.span.end.line += line_offset;
                }
                adjust_spans(&mut entry.value, line_offset);
            }
        }
        AstNode::Array(arr) => {
            arr.span.start.line += line_offset;
            arr.span.end.line += line_offset;
            for elem in &mut arr.elements {
                adjust_spans(elem, line_offset);
            }
        }
        AstNode::Function(func) => {
            func.span.start.line += line_offset;
            func.span.end.line += line_offset;
            adjust_spans(&mut func.args, line_offset);
        }
        AstNode::String(s) => { s.span.start.line += line_offset; s.span.end.line += line_offset; }
        AstNode::Number(n) => { n.span.start.line += line_offset; n.span.end.line += line_offset; }
        AstNode::Bool(b) => { b.span.start.line += line_offset; b.span.end.line += line_offset; }
        AstNode::Null(n) => { n.span.start.line += line_offset; n.span.end.line += line_offset; }
    }
}

/// Merge an entry into the appropriate parent object based on indentation.
fn merge_entry_into_parent(root: &mut ObjectNode, entry: ObjectEntry, indent: usize) {
    if indent == 0 {
        // Top-level entry
        root.entries.push(entry);
        return;
    }
    // Find the last entry at a lower indent level and merge into it
    for existing in root.entries.iter_mut().rev() {
        if let AstNode::Object(ref mut child_obj) = existing.value {
            child_obj.entries.push(entry);
            return;
        }
    }
    // Fallback: add to root
    root.entries.push(entry);
}

// ── JSON parsing via json-spanned-value ──

use json_spanned_value::spanned;

fn convert_json_spanned(value: &spanned::Value, idx: &LineIndex) -> AstNode {
    let span = idx.span(value.start()..value.end());

    match value.get_ref() {
        json_spanned_value::Value::Object(map) => {
            if map.len() == 1 {
                if let Some((key, val)) = map.iter().next() {
                    let key_str: &str = key.get_ref();
                    if CFN_FUNCTIONS.contains(&key_str) {
                        return AstNode::Function(FunctionNode {
                            name: key_str.to_string(),
                            args: Box::new(convert_json_spanned(val, idx)),
                            span,
                        });
                    }
                }
            }
            let mut entries = Vec::new();
            for (key, val) in map.iter() {
                let key_str: &str = key.get_ref();
                let key_span = idx.span(key.start()..key.end());
                entries.push(ObjectEntry {
                    key_node: AstNode::String(StringNode { value: key_str.to_string(), span: key_span }),
                    key: key_str.to_string(),
                    value: convert_json_spanned(val, idx),
                    key_span,
                });
            }
            AstNode::Object(ObjectNode { entries, span })
        }
        json_spanned_value::Value::Array(arr) => AstNode::Array(ArrayNode {
            elements: arr.iter().map(|v| convert_json_spanned(v, idx)).collect(),
            span,
        }),
        json_spanned_value::Value::String(s) => AstNode::String(StringNode {
            value: s.clone(),
            span,
        }),
        json_spanned_value::Value::Number(n) => AstNode::Number(NumberNode {
            value: n.as_f64().unwrap_or(0.0),
            span,
        }),
        json_spanned_value::Value::Bool(b) => AstNode::Bool(BoolNode {
            value: *b,
            span,
        }),
        json_spanned_value::Value::Null => AstNode::Null(NullNode { span }),
    }
}

/// Parse JSON text into an AstNode.
pub fn parse_json(input: &str) -> Result<AstNode, ParseError> {
    let value: spanned::Value = json_spanned_value::from_str(input)?;
    let idx = LineIndex::new(input);
    Ok(convert_json_spanned(&value, &idx))
}

/// Parse JSON leniently — fix trailing commas, unclosed braces, empty lines.
pub fn parse_json_lenient(input: &str) -> (Option<AstNode>, Vec<String>) {
    match parse_json(input) {
        Ok(node) => return (Some(node), vec![]),
        Err(_) => {}
    }

    let mut errors = Vec::new();
    let mut fixed = input.to_string();

    // Fix 1: Remove trailing commas before } or ]
    loop {
        let prev = fixed.clone();
        fixed = fixed.replace(", }", " }").replace(",}", "}").replace(", ]", " ]").replace(",]", "]");
        // Also handle whitespace/newlines between comma and closing
        let re_obj = regex_trailing_comma(&fixed, '}');
        if let Some(f) = re_obj { fixed = f; }
        let re_arr = regex_trailing_comma(&fixed, ']');
        if let Some(f) = re_arr { fixed = f; }
        if fixed == prev { break; }
    }

    // Fix 2: Remove empty lines (lines with only whitespace)
    let lines: Vec<&str> = fixed.lines().collect();
    let fixed: String = lines.iter()
        .filter(|l| !l.trim().is_empty())
        .cloned()
        .collect::<Vec<_>>()
        .join("\n");

    if let Ok(node) = parse_json(&fixed) {
        errors.push("JSON repaired (trailing commas or empty lines removed)".to_string());
        return (Some(node), errors);
    }

    // Fix 3: Try closing unclosed braces/brackets
    let mut open_braces = 0i32;
    let mut open_brackets = 0i32;
    let mut in_string = false;
    let mut escape_next = false;
    for ch in fixed.chars() {
        if escape_next {
            escape_next = false;
            continue;
        }
        if in_string {
            if ch == '\\' { escape_next = true; }
            else if ch == '"' { in_string = false; }
            continue;
        }
        if ch == '"' { in_string = true; continue; }
        match ch {
            '{' => open_braces += 1,
            '}' => open_braces -= 1,
            '[' => open_brackets += 1,
            ']' => open_brackets -= 1,
            _ => {}
        }
    }
    let mut closed = fixed.clone();
    for _ in 0..open_brackets { closed.push(']'); }
    for _ in 0..open_braces { closed.push('}'); }

    if let Ok(node) = parse_json(&closed) {
        errors.push("JSON repaired (unclosed braces/brackets)".to_string());
        return (Some(node), errors);
    }

    errors.push("JSON parse failed".to_string());
    (None, errors)
}

/// Remove trailing comma before a closing delimiter, handling whitespace/newlines.
fn regex_trailing_comma(input: &str, closing: char) -> Option<String> {
    let bytes = input.as_bytes();
    let mut result = Vec::from(bytes);
    let mut changed = false;
    let mut i = 0;
    while i < result.len() {
        if result[i] == b',' {
            // Look ahead past whitespace/newlines for closing delimiter
            let mut j = i + 1;
            while j < result.len() && (result[j] == b' ' || result[j] == b'\n' || result[j] == b'\r' || result[j] == b'\t') {
                j += 1;
            }
            if j < result.len() && result[j] == closing as u8 {
                result[i] = b' '; // Replace comma with space
                changed = true;
            }
        }
        i += 1;
    }
    if changed { Some(String::from_utf8(result).ok()?) } else { None }
}

/// Parse text as YAML or JSON (auto-detect by first non-whitespace char).
pub fn parse(input: &str) -> Result<AstNode, ParseError> {
    let trimmed = input.trim_start();
    if trimmed.starts_with('{') || trimmed.starts_with('[') {
        parse_json(input)
    } else {
        parse_yaml(input)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::context::Context;
    use std::sync::Arc;

    #[test]
    fn test_parse_yaml_template() {
        let template = "AWSTemplateFormatVersion: '2010-09-09'\nParameters:\n  Env:\n    Type: String\nResources:\n  MyBucket:\n    Type: AWS::S3::Bucket\nOutputs:\n  BucketArn:\n    Value: !GetAtt MyBucket.Arn";
        let node = parse(template).unwrap();
        let ctx = Context::from_ast(Arc::new(node));
        assert!(ctx.parameters.contains_key("Env"));
        assert!(ctx.resources.contains_key("MyBucket"));
        assert!(ctx.outputs.contains_key("BucketArn"));
    }

    #[test]
    fn test_parse_yaml_tags() {
        let template = "Value: !Ref MyParam";
        let node = parse_yaml(template).unwrap();
        let value = node.get("Value").unwrap();
        let func = value.as_function().unwrap();
        assert_eq!(func.name, "Ref");
        assert_eq!(func.args.as_str(), Some("MyParam"));
    }

    #[test]
    fn test_tagged_scalar_span_covers_tag() {
        let template = "TopicName: !Ref Environment";
        let node = parse_yaml(template).unwrap();
        let value = node.get("TopicName").unwrap();
        let func = value.as_function().unwrap();
        assert_eq!(func.name, "Ref");
        let span = func.span;
        // "TopicName: !Ref Environment"
        //  0         1111111111222222222
        //  0123456789012345678901234567
        // All 0-based now
        assert_eq!(span.start.line, 0);
        // !Ref starts at col 11, but yaml-rust2 reports scalar at col 16 (1-based=16, 0-based=15)
        // tag "!Ref " is 5 chars, so func start = 15 - 5 = 10
        assert!(span.start.column <= 11, "span start col {} should be <= 11", span.start.column);
        assert!(span.end.column >= 25, "span end col {} should be >= 25", span.end.column);
    }

    #[test]
    fn test_parse_yaml11_booleans() {
        let template = "Value: yes";
        let node = parse_yaml(template).unwrap();
        let value = node.get("Value").unwrap();
        assert_eq!(value.as_bool(), Some(true));
    }

    #[test]
    fn test_parse_json_template() {
        let input = r#"{"AWSTemplateFormatVersion": "2010-09-09", "Resources": {"B": {"Type": "AWS::S3::Bucket"}}}"#;
        let node = parse_json(input).unwrap();
        let ctx = Context::from_ast(Arc::new(node));
        assert!(ctx.resources.contains_key("B"));
    }
}

    #[test]
    fn test_nested_object_spans() {
        let template = "Resources:\n  AppBucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      BucketName: test\n      VersioningConfiguration:\n        Status: Enabled\n\n      Tags:\n        - Key: Env\n          Value: dev";
        let node = parse_yaml(template).unwrap();

        let props = node.get("Resources").unwrap()
            .get("AppBucket").unwrap()
            .get("Properties").unwrap();
        let props_obj = props.as_object().unwrap();
        for (k, v) in props_obj.iter() {
            let s = v.span();
            eprintln!("  Properties.{}: {}:{} -> {}:{}", k, s.start.line, s.start.column, s.end.line, s.end.column);
        }

        use crate::traverse::{node_at_position, object_context_at_position};

        // Line 7 is the blank line between "Status: Enabled" and "Tags:"
        // At col 6 (Properties key indent) -> should get Properties
        let result = object_context_at_position(&node, 7, 6);
        eprintln!("object_context(7,6) -> {:?}", result.as_ref().map(|(_, p)| p));
        assert!(result.is_some(), "should find context on blank line");
        let (_, ctx_path) = result.unwrap();
        assert_eq!(ctx_path, vec!["Resources", "AppBucket", "Properties"],
            "col 6 on blank line should resolve to Properties, got: {:?}", ctx_path);

        // At col 8 (VC child indent) -> should get VersioningConfiguration
        let result2 = object_context_at_position(&node, 7, 8);
        eprintln!("object_context(7,8) -> {:?}", result2.as_ref().map(|(_, p)| p));
        assert!(result2.is_some(), "should find context at col 8");
        let (_, ctx_path2) = result2.unwrap();
        assert_eq!(ctx_path2, vec!["Resources", "AppBucket", "Properties", "VersioningConfiguration"],
            "col 8 on blank line should resolve to VC, got: {:?}", ctx_path2);
    }

    #[test]
    fn test_func_spans() {
        let yaml = "Value: !Ref Environment";
        let node = parse_yaml(yaml).unwrap();
        let val = node.get("Value").unwrap();
        if let crate::node::AstNode::Function(f) = val {
            eprintln!("func name={} span={}:{}-{}:{}", f.name, f.span.start.line, f.span.start.column, f.span.end.line, f.span.end.column);
            let args_span = f.args.span();
            eprintln!("args span={}:{}-{}:{}", args_span.start.line, args_span.start.column, args_span.end.line, args_span.end.column);
        }

        let yaml2 = "Value: !GetAtt MyBucket.Arn";
        let node2 = parse_yaml(yaml2).unwrap();
        let val2 = node2.get("Value").unwrap();
        if let crate::node::AstNode::Function(f) = val2 {
            eprintln!("getatt dot: name={} args={:?}", f.name, f.args);
        }

        // Inline array form
        let yaml3 = "Value: !GetAtt [MyBucket, Arn]";
        let node3 = parse_yaml(yaml3).unwrap();
        let val3 = node3.get("Value").unwrap();
        eprintln!("getatt inline array: {:?}", val3);

        // Block array form
        let yaml4 = "Value:\n  Fn::GetAtt:\n    - MyBucket\n    - Arn";
        let node4 = parse_yaml(yaml4).unwrap();
        let val4 = node4.get("Value").unwrap();
        eprintln!("getatt block: {:?}", val4);

        // Plain string
        let yaml5 = "Type: AWS::S3::Bucket";
        let node5 = parse_yaml(yaml5).unwrap();
        let val5 = node5.get("Type").unwrap();
        let s = val5.span();
        eprintln!("string span={}:{}-{}:{}", s.start.line, s.start.column, s.end.line, s.end.column);
    }
