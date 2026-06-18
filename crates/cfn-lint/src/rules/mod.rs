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
