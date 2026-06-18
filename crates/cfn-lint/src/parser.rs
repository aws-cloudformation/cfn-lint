pub use cfn_ast::parser::ParseError;

/// Parse YAML or JSON bytes into an AstNode.
pub fn parse(input: &[u8]) -> Result<cfn_ast::node::AstNode, ParseError> {
    let text = std::str::from_utf8(input)
        .map_err(|e| ParseError::Yaml(format!("Invalid UTF-8: {}", e)))?;
    cfn_ast::parser::parse(text)
}

/// Parse JSON bytes into an AstNode.
pub fn parse_json(input: &[u8]) -> Result<cfn_ast::node::AstNode, ParseError> {
    let text = std::str::from_utf8(input)
        .map_err(|e| ParseError::Yaml(format!("Invalid UTF-8: {}", e)))?;
    cfn_ast::parser::parse_json(text)
}

/// Detect non-string mapping keys in a parsed AST (e.g. `!ImportValue Fn::Sub:` creates
/// a function node as a mapping key, which Python reports as E0000 "Unhashable type").
pub fn detect_non_string_keys(
    ast: &cfn_ast::node::AstNode,
) -> Vec<crate::jsonschema::ValidationError> {
    use crate::jsonschema::ValidationError;
    use cfn_ast::node::AstNode;

    let mut issues = Vec::new();
    fn walk(node: &AstNode, issues: &mut Vec<ValidationError>) {
        if !issues.is_empty() {
            return;
        } // Python stops at first unhashable key
        match node {
            AstNode::Object(obj) => {
                for entry in obj.non_string_key_entries() {
                    let k = &entry.key;
                    // Only flag function/object keys (unhashable types).
                    // Integer/boolean/null keys are valid YAML mapping keys.
                    if !k.contains("(...)") && !k.contains("{...}") {
                        continue;
                    }
                    let span = entry.key_span;
                    issues.push(ValidationError {
                        rule_id: Some("E0000".to_string()),
                        message: format!("Unhashable type \"{}\" (line {})", k, span.start.line),
                        path: vec![],
                        span,
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                    return;
                }
                for v in obj.values() {
                    walk(v, issues);
                    if !issues.is_empty() {
                        return;
                    }
                }
            }
            AstNode::Array(arr) => {
                for e in &arr.elements {
                    walk(e, issues);
                    if !issues.is_empty() {
                        return;
                    }
                }
            }
            AstNode::Function(f) => {
                walk(&f.args, issues);
            }
            _ => {}
        }
    }
    walk(ast, &mut issues);
    issues
}

/// Detect duplicate keys in YAML/JSON input.
pub fn detect_duplicate_keys(input: &[u8]) -> Vec<crate::jsonschema::ValidationError> {
    let text = match std::str::from_utf8(input) {
        Ok(t) => t,
        Err(_) => return Vec::new(),
    };
    let trimmed = text.trim_start();
    if trimmed.starts_with('{') {
        detect_duplicate_keys_json(text)
    } else {
        detect_duplicate_keys_yaml(text)
    }
}

fn make_issue(key: &str, line: u32, col: u32) -> crate::jsonschema::ValidationError {
    use crate::jsonschema::ValidationError;
    use cfn_ast::node::{Position, Span};
    ValidationError {
        rule_id: Some("E0000".to_string()),
        message: format!("Duplicate found \"{}\"", key),
        path: vec![],
        span: Span {
            start: Position { line, column: col },
            end: Position { line, column: col },
        },
        keyword: String::new(),
        unknown: false,
        resolved_from_ref: false,
        context: vec![],
        schema_id: None,
    }
}

fn detect_duplicate_keys_yaml(text: &str) -> Vec<crate::jsonschema::ValidationError> {
    use cfn_ast::yaml::parser::{Event, MarkedEventReceiver, Parser};
    use cfn_ast::yaml::scanner::Marker;
    use std::collections::HashMap;

    struct DupDetector {
        /// Stack of (keys_seen, expecting_key) per mapping level.
        /// keys_seen maps key_name -> (marker, already_reported_as_dup)
        stack: Vec<(HashMap<String, (Marker, bool)>, bool)>,
        issues: Vec<crate::jsonschema::ValidationError>,
        /// Track nesting for sequences to know we're not in a mapping
        in_sequence: Vec<bool>,
    }

    impl MarkedEventReceiver for DupDetector {
        fn on_event(&mut self, ev: Event, mark: Marker) {
            match ev {
                Event::MappingStart(_, _) => {
                    // If we're inside a mapping and expecting a value, this mapping IS the value
                    if let Some(top) = self.stack.last_mut() {
                        if !top.1 {
                            // We were expecting a value, now we got it (a nested mapping)
                            top.1 = true; // next scalar in parent will be a key again
                        }
                    }
                    self.stack.push((HashMap::new(), true)); // true = expecting key
                    self.in_sequence.push(false);
                }
                Event::MappingEnd => {
                    self.stack.pop();
                    self.in_sequence.pop();
                }
                Event::SequenceStart(_, _) => {
                    // If inside a mapping expecting value, consume it
                    if let Some(top) = self.stack.last_mut() {
                        if !top.1 {
                            top.1 = true;
                        }
                    }
                    self.in_sequence.push(true);
                }
                Event::SequenceEnd => {
                    self.in_sequence.pop();
                }
                Event::Scalar(ref key, _, _, _) => {
                    // Are we inside a sequence? Then this scalar is a sequence element, not a key
                    if self.in_sequence.last() == Some(&true) {
                        return;
                    }
                    if let Some(top) = self.stack.last_mut() {
                        if top.1 {
                            // Expecting a key
                            if let Some(existing) = top.0.get_mut(key) {
                                // Duplicate!
                                if !existing.1 {
                                    // First time seeing a dup of this key — report original too
                                    let orig_mark = existing.0;
                                    self.issues.push(make_issue(
                                        key,
                                        orig_mark.line() as u32,
                                        orig_mark.col() as u32,
                                    ));
                                    existing.1 = true;
                                }
                                self.issues.push(make_issue(
                                    key,
                                    mark.line() as u32,
                                    mark.col() as u32,
                                ));
                            } else {
                                top.0.insert(key.clone(), (mark, false));
                            }
                            top.1 = false; // next scalar is a value
                        } else {
                            // This scalar is a value
                            top.1 = true; // next scalar is a key
                        }
                    }
                }
                _ => {}
            }
        }
    }

    let mut detector = DupDetector {
        stack: Vec::new(),
        issues: Vec::new(),
        in_sequence: Vec::new(),
    };
    let mut parser = Parser::new_from_str(text);
    let _ = parser.load(&mut detector, true);
    detector.issues
}

fn detect_duplicate_keys_json(text: &str) -> Vec<crate::jsonschema::ValidationError> {
    use std::collections::HashMap;

    let bytes = text.as_bytes();
    let len = bytes.len();
    let mut i = 0;
    let mut line: u32 = 1;
    let mut col: u32 = 1;

    // Stack entry: Some(map) for objects, None for arrays
    let mut stack: Vec<Option<HashMap<String, (u32, u32, bool)>>> = Vec::new();
    let mut issues = Vec::new();
    let mut expect_key = false;

    while i < len {
        match bytes[i] {
            b'{' => {
                stack.push(Some(HashMap::new()));
                expect_key = true;
                col += 1;
                i += 1;
            }
            b'}' => {
                stack.pop();
                col += 1;
                i += 1;
            }
            b'[' => {
                stack.push(None);
                expect_key = false;
                col += 1;
                i += 1;
            }
            b']' => {
                stack.pop();
                col += 1;
                i += 1;
            }
            b':' => {
                expect_key = false;
                col += 1;
                i += 1;
            }
            b',' => {
                // After comma: expect key if in object, not if in array
                expect_key = matches!(stack.last(), Some(Some(_)));
                col += 1;
                i += 1;
            }
            b'"' => {
                let str_line = line;
                let str_col = col;
                i += 1;
                col += 1;
                let mut s = String::new();
                while i < len && bytes[i] != b'"' {
                    if bytes[i] == b'\\' && i + 1 < len {
                        s.push(bytes[i + 1] as char);
                        i += 2;
                        col += 2;
                    } else {
                        if bytes[i] == b'\n' {
                            line += 1;
                            col = 1;
                        } else {
                            col += 1;
                        }
                        s.push(bytes[i] as char);
                        i += 1;
                    }
                }
                if i < len {
                    i += 1;
                    col += 1;
                }

                if expect_key {
                    if let Some(Some(map)) = stack.last_mut() {
                        if let Some(existing) = map.get_mut(&s) {
                            if !existing.2 {
                                issues.push(make_issue(&s, existing.0, existing.1));
                                existing.2 = true;
                            }
                            issues.push(make_issue(&s, str_line, str_col));
                        } else {
                            map.insert(s, (str_line, str_col, false));
                        }
                    }
                }
            }
            b'\n' => {
                line += 1;
                col = 1;
                i += 1;
            }
            b'\r' => {
                line += 1;
                col = 1;
                i += 1;
                if i < len && bytes[i] == b'\n' {
                    i += 1;
                }
            }
            _ => {
                col += 1;
                i += 1;
            }
        }
    }

    issues
}
