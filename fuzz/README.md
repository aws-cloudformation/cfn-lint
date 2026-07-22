# Fuzzing

[cargo-fuzz](https://rust-fuzz.github.io/book/cargo-fuzz.html) (libFuzzer)
targets for the `cfn-ast` parser and the `cfn-lint` template layer, which
consume untrusted input.

## Targets

| Target           | Entry point                                                       | Covers |
|------------------|-------------------------------------------------------------------|--------|
| `ast_parse`      | `cfn_ast::parser::{parse, parse_yaml, parse_json, *_lenient}` + `traverse` | The hand-rolled YAML/JSON scanner → parser → `AstNode`, plus tree traversal. |
| `template_parse` | `cfn_lint::parser::parse` → `cfn_lint::template::Template::from_ast` | AST → structured `Template` conversion on top of a raw parse. |

## Prerequisites

```bash
rustup toolchain install nightly
cargo install cargo-fuzz --locked
```

## Running locally

```bash
# Seed the corpora from the repo's template fixtures (idempotent).
./fuzz/seed-corpus.sh

# Fuzz a single target (Ctrl-C to stop).
cargo fuzz run ast_parse
cargo fuzz run template_parse

# Time-boxed run, e.g. 20 minutes, with a per-input timeout:
cargo fuzz run ast_parse -- -max_total_time=1200 -timeout=25
```

Crashes are written to `fuzz/artifacts/<target>/`. Reproduce one with:

```bash
cargo fuzz run <target> fuzz/artifacts/<target>/crash-<hash>
```

## CI

[`.github/workflows/fuzz.yml`](../.github/workflows/fuzz.yml) runs a short pass
of each target on a weekly cron (and on manual `workflow_dispatch`), uploading
any crash artifacts. It is intentionally a smoke-level run — deep campaigns
should be run locally or on a dedicated fuzzing service.
