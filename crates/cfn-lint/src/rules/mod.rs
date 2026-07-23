pub mod conditions;
pub mod mappings;
pub mod metadata;
pub mod outputs;
pub mod parameters;
pub mod resources;
pub mod templates;
pub mod transforms;

// Re-export all submodules so existing `crate::rules::e3015` style paths continue to work
pub use conditions::*;
pub use mappings::*;
pub use metadata::*;
pub use outputs::*;
pub use parameters::*;
pub use resources::*;
pub use templates::*;
pub use transforms::*;

/// Register a CfnLintRule for automatic discovery via inventory.
/// For fully migrated rules (implementing CfnLintRule directly).
/// Usage: `register_cfn_lint_rule!(E3005);`
#[macro_export]
macro_rules! register_cfn_lint_rule {
    ($rule:expr) => {
        inventory::submit! { &$rule as &'static dyn $crate::jsonschema::cfn_lint_keyword::CfnLintRule }
    };
}

/// Macro for extension schema rules that validate resource properties against
/// a JSON Schema file embedded at compile time. Handles both regional schemas
/// (keyed by region) and non-regional schemas.
///
/// Each invocation generates a struct implementing `CfnLintRule` for keyword-based
/// dispatch during schema validation.
///
/// # Why 77 per-file invocations instead of one central table?
///
/// A code review raised whether the ~77 single-invocation files (plus their
/// `mod.rs` entries) could collapse into one declarative table (a `const`
/// array + generation loop, or a build script). This was investigated and
/// **intentionally not done**, because the deciding factor is `schema_path`:
///
/// - Each rule embeds its schema with `include_str!($schema_path)`.
///   `include_str!` requires a **string-literal** path resolved **relative to
///   the source file that contains the invocation**. Rules live in per-resource
///   directories (`rules/resources/<service>/`) and reference schemas via
///   directory-relative paths (e.g.
///   `"../../../../data/schemas/extensions/aws_dynamodb_table/..."`), keeping
///   each schema co-located with the rule that uses it.
/// - A central `const` table cannot carry `include_str!` contents keyed
///   generically: every path would have to be relative to the **one** table
///   file, collapsing the per-directory relative-include ergonomics into a
///   single fragile flat prefix and destroying schema co-location.
/// - A build-script code generator could emit the invocations, but moves the
///   rule inventory out of the source tree into generated code (harder to read,
///   grep, and review) for marginal gain — each rule is already an ~8-line
///   declarative block.
///
/// The only remaining boilerplate is the one-line `pub mod eXXXX;` entry per
/// rule, which is trivial and — crucially — a *forgotten* entry is now caught
/// by the registration-completeness snapshot test
/// (`tests/rule_registration.rs`). So the tradeoff of a central registry is bad
/// and the per-file invocation pattern is kept.
#[macro_export]
macro_rules! extension_schema_rule {
    // Variant with explicit property path (for regional schemas targeting a specific property)
    (
        $struct_name:ident,
        id: $id:expr,
        description: $desc:expr,
        severity: $sev:expr,
        resource_type: $resource_type:expr,
        schema_path: $schema_path:expr,
        regional: $regional:expr,
        property: $property:expr
    ) => {
        pub struct $struct_name;

        impl $crate::jsonschema::cfn_lint_keyword::CfnLintRule for $struct_name {
            fn id(&self) -> &str { $id }
            fn short_description(&self) -> &str { $desc }
            fn description(&self) -> &str { $desc }
            fn severity(&self) -> $crate::rules::Severity { $sev }
            fn keywords(&self) -> &[&str] {
                static KEYWORDS: &[&str] = &[concat!("Resources/", $resource_type, "/Properties/", $property)];
                KEYWORDS
            }
            fn validate(
                &self,
                validator: &$crate::jsonschema::Validator,
                _keyword: &str,
                instance: &$crate::ast::AstNode,
                _schema: &serde_json::Value,
                path: &[String],
            ) -> Vec<$crate::jsonschema::ValidationError> {
                use std::sync::LazyLock;
                static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
                    serde_json::from_str(include_str!($schema_path)).unwrap_or_default()
                });

                // Skip validation if the instance is an unresolved function
                if instance.as_function().is_some() {
                    return vec![];
                }

                if $regional {
                    $crate::jsonschema::json_schema_rule::validate_regional(
                        $id, $desc, validator, instance, &SCHEMA, path
                    )
                } else {
                    $crate::jsonschema::json_schema_rule::validate_schema(
                        $id, $desc, validator, instance, &SCHEMA, path
                    )
                }
            }
        }

        $crate::register_cfn_lint_rule!($struct_name);
    };
    // Original variant without property (for schemas targeting Properties object)
    (
        $struct_name:ident,
        id: $id:expr,
        description: $desc:expr,
        severity: $sev:expr,
        resource_type: $resource_type:expr,
        schema_path: $schema_path:expr,
        regional: $regional:expr
    ) => {
        pub struct $struct_name;

        impl $crate::jsonschema::cfn_lint_keyword::CfnLintRule for $struct_name {
            fn id(&self) -> &str { $id }
            fn short_description(&self) -> &str { $desc }
            fn description(&self) -> &str { $desc }
            fn severity(&self) -> $crate::rules::Severity { $sev }
            fn keywords(&self) -> &[&str] {
                static KEYWORDS: &[&str] = &[concat!("Resources/", $resource_type, "/Properties")];
                KEYWORDS
            }
            fn validate(
                &self,
                validator: &$crate::jsonschema::Validator,
                _keyword: &str,
                instance: &$crate::ast::AstNode,
                _schema: &serde_json::Value,
                path: &[String],
            ) -> Vec<$crate::jsonschema::ValidationError> {
                use std::sync::LazyLock;
                static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
                    serde_json::from_str(include_str!($schema_path)).unwrap_or_default()
                });

                if instance.as_function().is_some() {
                    return vec![];
                }

                if $regional {
                    $crate::jsonschema::json_schema_rule::validate_regional(
                        $id, $desc, validator, instance, &SCHEMA, path
                    )
                } else {
                    $crate::jsonschema::json_schema_rule::validate_schema(
                        $id, $desc, validator, instance, &SCHEMA, path
                    )
                }
            }
        }

        $crate::register_cfn_lint_rule!($struct_name);
    };
    // Multi-keyword variant for regional schemas with multiple dispatch paths
    (
        $struct_name:ident,
        id: $id:expr,
        description: $desc:expr,
        severity: $sev:expr,
        schema_path: $schema_path:expr,
        keywords: [$($kw:expr),+ $(,)?]
    ) => {
        pub struct $struct_name;

        impl $crate::jsonschema::cfn_lint_keyword::CfnLintRule for $struct_name {
            fn id(&self) -> &str { $id }
            fn short_description(&self) -> &str { $desc }
            fn description(&self) -> &str { $desc }
            fn severity(&self) -> $crate::rules::Severity { $sev }
            fn keywords(&self) -> &[&str] {
                &[$($kw),+]
            }
            fn validate(
                &self,
                validator: &$crate::jsonschema::Validator,
                _keyword: &str,
                instance: &$crate::ast::AstNode,
                _schema: &serde_json::Value,
                path: &[String],
            ) -> Vec<$crate::jsonschema::ValidationError> {
                use std::sync::LazyLock;
                static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
                    serde_json::from_str(include_str!($schema_path)).unwrap_or_default()
                });

                if instance.as_function().is_some() {
                    return vec![];
                }

                $crate::jsonschema::json_schema_rule::validate_regional(
                    $id, $desc, validator, instance, &SCHEMA, path
                )
            }
        }

        $crate::register_cfn_lint_rule!($struct_name);
    };
}

/// Declarative macro for "anchor" rules: no-op metadata holders whose actual
/// validation is performed elsewhere in the pipeline (the parser, the schema
/// validation pipeline, a `format` keyword handler, or the engine's condition
/// checks).
///
/// Each anchor exists purely so its rule ID is registered — this makes the ID
/// visible to `--list-rules` and available for include/exclude configuration,
/// and lets the registration-completeness snapshot test
/// (`tests/rule_registration.rs`) detect an accidental drop or duplicate.
///
/// Modeled on [`extension_schema_rule!`]. The rule ID is derived from the
/// struct name (which must equal the ID, e.g. `E1150`), collapsing a ~40-line
/// hand-written struct into a single invocation.
///
/// Usage:
/// ```ignore
/// use crate::rules::Severity;
/// crate::anchor_rule!(
///     E1150,
///     "Validate security group format",
///     "Security groups must ref/getatt to a security group or match the valid pattern",
///     Severity::Error
/// );
/// ```
#[macro_export]
macro_rules! anchor_rule {
    (
        $struct_name:ident,
        $short:expr,
        $desc:expr,
        $sev:expr $(,)?
    ) => {
        /// Anchor rule: a no-op metadata holder whose actual validation is
        /// performed elsewhere in the pipeline (parser, schema pipeline,
        /// `format` keyword handler, or engine condition checks). Registered so
        /// its rule ID appears in `--list-rules` and can be included/excluded
        /// via configuration. See the invocation site for where validation
        /// actually happens.
        pub struct $struct_name;

        impl $crate::jsonschema::cfn_lint_keyword::CfnLintRule for $struct_name {
            fn id(&self) -> &str {
                stringify!($struct_name)
            }
            fn short_description(&self) -> &str {
                $short
            }
            fn description(&self) -> &str {
                $desc
            }
            fn severity(&self) -> $crate::rules::Severity {
                $sev
            }
            fn keywords(&self) -> &[&str] {
                &["/"]
            }
            fn validate_template(
                &self,
                _template: &$crate::template::Template,
                _root: &$crate::ast::AstNode,
            ) -> Vec<$crate::jsonschema::ValidationError> {
                vec![]
            }
        }

        $crate::register_cfn_lint_rule!($struct_name);
    };
}

use std::fmt;

use crate::ast::Span;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Severity {
    Error,
    Warning,
    Informational,
}

impl fmt::Display for Severity {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Severity::Error => write!(f, "E"),
            Severity::Warning => write!(f, "W"),
            Severity::Informational => write!(f, "I"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct Issue {
    pub rule_id: String,
    pub message: String,
    pub path: Vec<String>,
    pub span: Span,
    pub severity: Severity,
}

impl fmt::Display for Issue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{}:{}: [{}] {} ({})",
            self.span.start.line, self.span.start.column, self.severity, self.message, self.rule_id
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::Position;

    #[test]
    fn test_severity_display() {
        assert_eq!(format!("{}", Severity::Error), "E");
        assert_eq!(format!("{}", Severity::Warning), "W");
        assert_eq!(format!("{}", Severity::Informational), "I");
    }

    #[test]
    fn test_issue_display() {
        let issue = Issue {
            rule_id: "E1003".to_string(),
            message: "Too long".to_string(),
            path: vec!["Description".to_string()],
            span: Span {
                start: Position { line: 2, column: 1 },
                end: Position { line: 2, column: 1 },
            },
            severity: Severity::Error,
        };
        assert_eq!(format!("{}", issue), "2:1: [E] Too long (E1003)");
    }
}
