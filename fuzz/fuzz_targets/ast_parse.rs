#![no_main]
//! Fuzz target for the hand-rolled cfn-ast YAML/JSON scanner + parser.
//!
//! Drives arbitrary input through every public parse entry point of the
//! `cfn-ast` crate (`Scanner` -> parser -> `AstNode`). libFuzzer treats any
//! panic or timeout as a crash, so this shakes out unhandled `unwrap`/`panic!`,
//! integer overflows, unbounded recursion, and pathological hangs in the
//! forked YAML layer.

use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // The cfn-ast scanner operates on `&str`. A CloudFormation template is
    // always UTF-8, so non-UTF-8 input is not interesting here; the byte
    // oriented `cfn_lint::parser` entry point is fuzzed in `template_parse`.
    let Ok(text) = std::str::from_utf8(data) else {
        return;
    };

    // Strict auto-detecting entry point (Scanner -> parser -> AST).
    if let Ok(ast) = cfn_ast::parser::parse(text) {
        // Exercise the traversal recursion + path accumulation (C10 fix path).
        cfn_ast::traverse::walk(&ast, &[], &mut |_node, _path| true);
        // Span-based search recursion.
        let _ = cfn_ast::traverse::node_at_position(&ast, 0, 0);
    }

    // Drive both scanners directly, independent of auto-detection.
    let _ = cfn_ast::parser::parse_yaml(text);
    let _ = cfn_ast::parser::parse_json(text);

    // Lenient recovery variants have their own error-unwinding logic
    // (partial-AST reconstruction / input rewriting) worth fuzzing.
    let _ = cfn_ast::parser::parse_yaml_lenient(text);
    let _ = cfn_ast::parser::parse_json_lenient(text);
});
