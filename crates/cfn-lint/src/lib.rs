//! cfn-lint core library.
//!
//! # Public API surface
//!
//! The modules below marked `pub` form the intended, supported public API —
//! this is what the `cfn-lint` binary, the `cfn-lint-py` Python bindings, the
//! benchmarks, and the integration tests consume:
//!
//! - [`ast`] — template AST node types (`AstNode`, `Span`, ...).
//! - [`config`] — configuration (`Config`, `ConfigOverrides`).
//! - [`custom_rules`] — custom-rule loading (`load_custom_rules`).
//! - [`engine`] — the linting engine (`Engine`).
//! - [`formatters`] — output formatters (`get_formatter`, `Formatter`, `ValidationResult`).
//! - [`jsonschema`] — schema validation types (`Validator`, `ValidationError`, `KeywordRuleRegistry`).
//! - [`parser`] — template parsing (`parse`).
//! - [`rules`] — rule severity and the rule structs/macros.
//! - [`schema`] — schema management (`update_schemas`).
//! - [`template`] — the parsed `Template` model.
//!
//! Everything else is an implementation detail. Those modules are marked
//! `pub(crate)` where they are used only within this crate, or
//! `#[doc(hidden)] pub` where their types must remain reachable because they
//! appear in the signatures of the public API above. `#[doc(hidden)]` /
//! `pub(crate)` items are **not** part of the stable API and may change without
//! notice — external consumers should not depend on them.

// --- Public API ------------------------------------------------------------
pub mod ast;
pub mod cli;
pub mod config;
pub mod custom_rules;
pub mod engine;
pub mod formatters;
pub mod jsonschema;
pub mod parser;
pub mod rules;
pub mod schema;
pub mod template;

// --- Internal implementation details ---------------------------------------
// Not part of the supported public API. `#[doc(hidden)] pub` is used (rather
// than `pub(crate)`) for modules whose types surface in the signatures of the
// public API above, which keeps them reachable without a `private_interfaces`
// warning while still hiding them from the generated docs.
#[doc(hidden)]
pub mod conditions;
#[doc(hidden)]
pub mod context;
#[doc(hidden)]
pub mod getatts;
#[doc(hidden)]
pub mod graph;
#[doc(hidden)]
pub mod helpers;
#[doc(hidden)]
pub mod resolver;
#[doc(hidden)]
pub mod transform;
#[doc(hidden)]
pub mod walker;
