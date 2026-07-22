#![no_main]
//! Fuzz target for the CloudFormation template layer.
//!
//! Feeds arbitrary bytes through `cfn_lint::parser::parse` (which validates
//! UTF-8 and dispatches to the cfn-ast scanner) and then builds the structured
//! `Template` via `Template::from_ast`. This covers the AST -> Template
//! conversion (section parsing, resource/parameter extraction) on top of the
//! raw parse, catching panics that only surface once the parsed shape is
//! reinterpreted as a template.

use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // `cfn_lint::parser::parse` takes raw bytes and validates UTF-8 itself,
    // so arbitrary bytes can be fed straight through.
    if let Ok(ast) = cfn_lint::parser::parse(data) {
        // Reinterpret the parsed AST as a structured CloudFormation template.
        let _ = cfn_lint::template::Template::from_ast(&ast);
    }

    // Also drive the JSON-specific byte entry point directly.
    let _ = cfn_lint::parser::parse_json(data);
});
