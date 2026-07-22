# cfn-ast

A span-preserving Abstract Syntax Tree (AST) for CloudFormation templates,
parsed from either YAML or JSON. `cfn-ast` produces an `AstNode` tree that
retains source positions, duplicate keys, non-string keys, and CloudFormation
short-form intrinsic functions so that downstream linting can report precise,
Python-`cfn-lint`-compatible diagnostics.

Public entry points (`src/parser.rs`):

- `parse(&str)` — auto-detect YAML vs JSON by the first non-whitespace byte.
- `parse_yaml(&str)` / `parse_json(&str)` — force a specific parser.
- `parse_yaml_lenient` / `parse_json_lenient` — best-effort recovery that
  returns a partial AST plus a list of error strings.

## YAML layer provenance

The YAML scanner and parser under [`src/yaml/`](src/yaml/) are **forked from
[`yaml-rust2`](https://github.com/Ethiraric/yaml-rust2) v0.10.4**
(dual-licensed MIT OR Apache-2.0). The fork point is recorded at the top of
[`src/yaml/mod.rs`](src/yaml/mod.rs).

We forked rather than depended on the upstream crate because CloudFormation
templates are not strictly conformant YAML 1.2 documents: they rely on YAML 1.1
type resolution and CloudFormation-specific short tags, and `cfn-lint` needs to
preserve structure (duplicate/non-string keys, exact spans) that a standard
YAML loader discards or rejects. The fork also lets us build the span-carrying
`AstNode` directly from scanner events.

### CloudFormation-specific relaxations and deviations

The list below is the set of intentional divergences from upstream
`yaml-rust2`. When re-syncing with a newer upstream, re-apply these:

1. **Short-form intrinsic tags.** CloudFormation short tags such as `!Ref`,
   `!Sub`, `!GetAtt`, `!If`, `!Join`, `!Select`, `!Split`, `!FindInMap`,
   `!Base64`, `!Cidr`, `!GetAZs`, `!ImportValue`, `!Condition`, `!And`, `!Or`,
   `!Not`, `!Equals`, `!Transform`, `!ToJsonString`, `!Length`, `!ForEach`, and
   `!GetStackOutput` are resolved into `AstNode::Function` nodes (their
   `Fn::*` long form). See `YAML_TAG_MAP` / `resolve_tag` in `src/parser.rs`.

2. **YAML 1.1 boolean resolution.** Plain scalars `yes`/`no`, `on`/`off`
   (and their case variants), in addition to `true`/`false`, resolve to
   booleans, matching CloudFormation / PyYAML behavior. See
   `resolve_yaml11_bool` in `src/parser.rs`. (Upstream YAML 1.2 only treats
   `true`/`false` as booleans.)

3. **Relaxed quoted-scalar continuation-line indentation.** CloudFormation and
   PyYAML accept quoted scalars whose continuation lines are indented at any
   level; upstream `yaml-rust2` rejected this. See the note in
   `Scanner::scan_flow_scalar` (`src/yaml/scanner.rs`).

4. **Duplicate anchors are allowed.** An anchor name may be redefined/reused;
   upstream returned a "duplicated anchor" error. See `register_anchor` in
   `src/yaml/parser.rs`.

5. **Duplicate and non-string mapping keys are preserved, not merged or
   rejected.** `ObjectNode` keeps every entry in source order (see
   `duplicate_keys` / `non_string_key_entries` in `src/node.rs`) so that
   `cfn-lint` can emit `E0000` for duplicate keys and unhashable-type keys
   instead of silently collapsing them.

6. **Debug logging removed.** Upstream's `debug!` module is replaced by a
   no-op `debug_print!` macro (`src/yaml/scanner.rs`) to drop the dependency.

> **Security note:** this YAML layer consumes untrusted input. It is fuzzed
> continuously via [`../../fuzz/`](../../fuzz/) (cargo-fuzz targets + a weekly
> scheduled workflow). Run `cargo fuzz run ast_parse` before landing changes to
> the scanner/parser.

## Building & testing

```bash
cargo test -p cfn-ast
cargo clippy -p cfn-ast --all-targets
```

## License

`MIT-0`. The forked YAML layer additionally carries upstream `yaml-rust2`'s
`MIT OR Apache-2.0` terms.
