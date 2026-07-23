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

    /// Per-mapping-level entry: (keys_seen → (marker, already_reported_as_dup), expecting_key).
    type MappingLevel = (HashMap<String, (Marker, bool)>, bool);

    struct DupDetector {
        /// Stack of (keys_seen, expecting_key) per mapping level.
        /// keys_seen maps key_name -> (marker, already_reported_as_dup)
        stack: Vec<MappingLevel>,
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
                                    // yaml-rust2 Marker lines are 1-based; the
                                    // main parser (cfn-ast `marker_to_pos`) stores
                                    // 0-based lines via `.saturating_sub(1)`.
                                    // Columns are already 0-based in the scanner.
                                    self.issues.push(make_issue(
                                        key,
                                        orig_mark.line().saturating_sub(1) as u32,
                                        orig_mark.col() as u32,
                                    ));
                                    existing.1 = true;
                                }
                                self.issues.push(make_issue(
                                    key,
                                    mark.line().saturating_sub(1) as u32,
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
    // 0-based on both axes to match the main parser (cfn-ast `LineIndex::position`
    // reports 0-based line and column). `col` is reset to 0 (not 1) on every
    // newline below for the same reason.
    let mut line: u32 = 0;
    let mut col: u32 = 0;

    // Stack entry: Some(map) for objects, None for arrays.
    // Map value: (line, column, already_reported_as_dup).
    type ObjectKeyStack = Vec<Option<HashMap<String, (u32, u32, bool)>>>;
    let mut stack: ObjectKeyStack = Vec::new();
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
                            col = 0;
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
                col = 0;
                i += 1;
            }
            b'\r' => {
                line += 1;
                col = 0;
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

#[cfg(test)]
mod tests {
    use super::{detect_duplicate_keys, parse, parse_json};
    use crate::jsonschema::ValidationError;
    use cfn_ast::node::{AstNode, Position};

    /// Start positions of every top-level object entry whose key matches
    /// `key`, in source order — the exact positions the MAIN parser records
    /// for that key's span. `ObjectNode::entries` preserves duplicates.
    fn parser_key_positions(ast: &AstNode, key: &str) -> Vec<Position> {
        match ast {
            AstNode::Object(obj) => obj
                .entries
                .iter()
                .filter(|e| e.key == key)
                .map(|e| e.key_span.start)
                .collect(),
            _ => Vec::new(),
        }
    }

    fn detector_positions(issues: &[ValidationError]) -> Vec<Position> {
        issues.iter().map(|i| i.span.start).collect()
    }

    // C4: yaml-rust2 `Marker` lines are 1-based; the duplicate-key detector must
    // report 0-based lines to match cfn-ast `marker_to_pos`
    // (`line().saturating_sub(1)`, column left as the already-0-based `col()`).
    #[test]
    fn yaml_duplicate_key_positions_match_parser_convention() {
        // Byte layout (0-based lines; yaml columns are 0-based):
        //   line 0: `Dup: 1`    -> key `Dup` at (line 0, col 0)
        //   line 1: `Other: 2`
        //   line 2: `Dup: 3`    -> key `Dup` at (line 2, col 0)
        let template = b"Dup: 1\nOther: 2\nDup: 3\n";

        let issues = detect_duplicate_keys(template);
        assert_eq!(issues.len(), 2, "expected original + duplicate reports");
        for issue in &issues {
            assert_eq!(issue.rule_id.as_deref(), Some("E0000"));
            assert!(issue.message.contains("Duplicate found"));
        }

        // Concrete 0-based expectations. Before the C4 fix the lines were 1 and 3
        // (one line too low).
        let got = detector_positions(&issues);
        assert_eq!(got[0], Position { line: 0, column: 0 }); // first occurrence
        assert_eq!(got[1], Position { line: 2, column: 0 }); // duplicate

        // Cross-check: identical to the positions the MAIN parser records for
        // the key's span.
        let ast = parse(template).expect("template parses");
        for p in parser_key_positions(&ast, "Dup") {
            assert!(
                got.contains(&p),
                "detector positions {:?} must include main-parser key span start {:?}",
                got,
                p
            );
        }
    }

    // C5: the JSON scanner tracked 1-based line/col; the detector must report
    // 0-based on both axes to match cfn-ast `LineIndex::position`.
    #[test]
    fn json_duplicate_key_positions_match_parser_convention() {
        // Byte layout (0-based lines and columns, per cfn-ast `LineIndex`):
        //   line 0: `{`
        //   line 1: `  "Dup": 1,`    -> key opening quote at (line 1, col 2)
        //   line 2: `  "Other": 2,`
        //   line 3: `  "Dup": 3`     -> key opening quote at (line 3, col 2)
        //   line 4: `}`
        let template = b"{\n  \"Dup\": 1,\n  \"Other\": 2,\n  \"Dup\": 3\n}";

        let issues = detect_duplicate_keys(template);
        assert_eq!(issues.len(), 2, "expected original + duplicate reports");
        for issue in &issues {
            assert_eq!(issue.rule_id.as_deref(), Some("E0000"));
            assert!(issue.message.contains("Duplicate found"));
        }

        // Concrete 0-based expectations. Before the C5 fix these were (2,3) and
        // (4,3) — one too high on both axes.
        let got = detector_positions(&issues);
        assert_eq!(got[0], Position { line: 1, column: 2 }); // first occurrence
        assert_eq!(got[1], Position { line: 3, column: 2 }); // duplicate

        // The main JSON parser (serde) rejects duplicate keys outright, so we
        // cannot pull two key spans from one parse. Instead verify the detector
        // agrees with the main parser on a VALID template whose `"Dup"` key sits
        // at the identical byte layout (line 1, col 2).
        let valid = b"{\n  \"Dup\": 1\n}";
        let ast = parse_json(valid).expect("valid template parses");
        assert_eq!(
            parser_key_positions(&ast, "Dup"),
            vec![got[0]],
            "detector first-occurrence position must match main parser key span"
        );
    }

    // Guard the column reset: a duplicate key that is NOT on the first line must
    // still get a 0-based column (regression for the `col = 1` newline resets).
    #[test]
    fn json_duplicate_key_column_is_zero_based_after_newline() {
        // line 1: `    "K": 1,`  -> quote at col 4 (four leading spaces)
        // line 2: `    "K": 2`   -> quote at col 4
        let template = b"{\n    \"K\": 1,\n    \"K\": 2\n}";
        let issues = detect_duplicate_keys(template);
        let got = detector_positions(&issues);
        assert_eq!(got[0], Position { line: 1, column: 4 });
        assert_eq!(got[1], Position { line: 2, column: 4 });
    }
}
