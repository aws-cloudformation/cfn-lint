//! Robustness regression tests: the parser entry points must never panic on
//! well-formed *or* malformed input. These run on the stable toolchain in
//! normal CI and complement the nightly cargo-fuzz targets in `../../../fuzz/`
//! (which explore far more inputs but only run on a weekly schedule).
//!
//! If the fuzzer ever finds a crashing input, add its minimized bytes to
//! `ADVERSARIAL_INPUTS` (or as a dedicated `#[test]`) so the regression is
//! locked in on stable.

use std::path::PathBuf;

fn manifest_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

/// Feed a byte slice through every parser entry point exercised by the fuzz
/// targets. The assertion is implicit: a panic fails the test.
fn drive_all(bytes: &[u8]) {
    // Byte-oriented cfn-lint entry points.
    if let Ok(ast) = cfn_lint::parser::parse(bytes) {
        let _ = cfn_lint::template::Template::from_ast(&ast);
        cfn_ast::traverse::walk(&ast, &[], &mut |_, _| true);
        let _ = cfn_ast::traverse::node_at_position(&ast, 0, 0);
    }
    let _ = cfn_lint::parser::parse_json(bytes);

    // str-oriented cfn-ast entry points (only valid UTF-8).
    if let Ok(text) = std::str::from_utf8(bytes) {
        let _ = cfn_ast::parser::parse(text);
        let _ = cfn_ast::parser::parse_yaml(text);
        let _ = cfn_ast::parser::parse_json(text);
        let _ = cfn_ast::parser::parse_yaml_lenient(text);
        let _ = cfn_ast::parser::parse_json_lenient(text);
    }
}

/// Recursively collect template files under `dir`.
fn collect_templates(dir: &std::path::Path, out: &mut Vec<PathBuf>) {
    let Ok(entries) = std::fs::read_dir(dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        if path.is_dir() {
            collect_templates(&path, out);
        } else if matches!(
            path.extension().and_then(|e| e.to_str()),
            Some("yaml") | Some("yml") | Some("json") | Some("template")
        ) {
            out.push(path);
        }
    }
}

#[test]
fn corpus_templates_never_panic() {
    let mut files = Vec::new();
    collect_templates(&manifest_dir().join("tests/fixtures/templates"), &mut files);
    // tests/integration lives at the repo root (../../tests/integration).
    collect_templates(&manifest_dir().join("../../tests/integration"), &mut files);

    assert!(
        !files.is_empty(),
        "no seed templates found; expected fixtures/integration templates"
    );

    for path in &files {
        let bytes = std::fs::read(path).expect("failed to read template");
        drive_all(&bytes);
    }
}

/// Hand-crafted malformed / adversarial inputs that stress the scanner's edge
/// handling. None of these should panic (they may legitimately error).
const ADVERSARIAL_INPUTS: &[&[u8]] = &[
    b"",
    b" ",
    b"\n\n\n",
    b"\t",
    b"---",
    b"...",
    b"{",
    b"[",
    b"[{[{[{",
    b"{{{{{{{{",
    b"}]}]",
    b":",
    b"- - - -",
    b"key:",
    b"key: value: extra",
    b"!Ref",
    b"!Ref ",
    b"!UnknownTag foo",
    b"!!str 1",
    b"&a *a",
    b"*undefined",
    b"%TAG",
    b"%TAG ! !",
    b"%YAML 1.1",
    b"'unterminated",
    b"\"unterminated",
    b"\"\\",
    b"\"\\u",
    b"\"\\uZZZZ\"",
    b"a: &anchor\nb: *anchor\nc: &anchor 2\nd: *anchor",
    b"? complex\n: key",
    b"foo: |\n  block\n scalar",
    b"foo: >\n folded\n  text",
    b"[\xff\xfe]",
    b"\xc3\x28",       // invalid UTF-8 (lone continuation)
    b"key: \x00value", // embedded NUL
    b"# just a comment",
    b"{\"a\":\"b\",}",    // trailing comma (lenient JSON)
    b"{\"a\": {\"b\":}}", // missing value
    b"%C3%A9",            // percent-escape as plain scalar
    b"!<tag:%C3%A9> v",   // percent-escaped tag URI
];

#[test]
fn adversarial_inputs_never_panic() {
    for input in ADVERSARIAL_INPUTS {
        drive_all(input);
    }
}

#[test]
fn deeply_nested_input_is_bounded() {
    // Moderate nesting the parser is expected to handle without panicking.
    // (Unbounded-depth exploration is left to the fuzzer / DoS-limit task.)
    for depth in [64usize, 256, 512] {
        let flow_seq = format!("{}{}", "[".repeat(depth), "]".repeat(depth));
        drive_all(flow_seq.as_bytes());

        let flow_map = format!("{}{}", "{a: ".repeat(depth), "}".repeat(depth));
        drive_all(flow_map.as_bytes());

        let block = (0..depth)
            .map(|i| format!("{}k:", "  ".repeat(i)))
            .collect::<Vec<_>>()
            .join("\n");
        drive_all(block.as_bytes());
    }
}
