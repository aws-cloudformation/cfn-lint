pub mod cfn_lint_keyword;
mod filter;
pub mod json_schema_rule;
pub mod keywords;
pub mod resolvers;
mod validate;

use std::collections::HashMap;
use std::sync::Arc;

use crate::ast::{AstNode, Span};
use crate::context::Context;
use cfn_lint_keyword::KeywordRuleRegistry;

/// A validation error produced by schema validation.
#[derive(Debug, Clone, Default)]
pub struct ValidationError {
    /// Rule ID (e.g. "E3035"). None until assigned by a rule or keyword mapping.
    pub rule_id: Option<String>,
    pub message: String,
    pub path: Vec<String>,
    pub keyword: String,
    pub span: Span,
    /// When `true`, this error represents an unresolvable function.
    /// Used internally by composition keywords; filtered out before returning to callers.
    pub unknown: bool,
    /// When `true`, this error was produced for a value resolved from a Ref.
    pub resolved_from_ref: bool,
    /// Sub-errors from composition keywords (anyOf, oneOf, allOf, if/then/else).
    /// Mirrors Python's ValidationError.context.
    pub context: Vec<ValidationError>,
    /// Schema ID for composition tracking. The walker tags errors from anyOf/oneOf
    /// alternatives with the alternative's ID to filter on exit.
    pub schema_id: Option<usize>,
}

impl ValidationError {
    pub fn new(
        rule_id: impl Into<String>,
        message: impl Into<String>,
        path: Vec<String>,
        span: Span,
    ) -> Self {
        Self {
            rule_id: Some(rule_id.into()),
            message: message.into(),
            path,
            span,
            ..Default::default()
        }
    }

    pub fn schema_error(
        keyword: impl Into<String>,
        message: impl Into<String>,
        path: Vec<String>,
        span: Span,
    ) -> Self {
        Self {
            message: message.into(),
            path,
            span,
            keyword: keyword.into(),
            ..Default::default()
        }
    }
}

/// Result of validating a node against a schema.
#[derive(Debug, Clone)]
pub struct ValidationResult {
    pub valid: bool,
    pub errors: Vec<ValidationError>,
}

/// Signature for keyword validator functions.
pub type KeywordValidator = fn(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError>;

/// Non-validation keywords to skip during iteration.
const SKIP_KEYWORDS: &[&str] = &[
    "then",
    "else",
    "definitions",
    "$defs",
    "description",
    "title",
    "$ref",
    "$schema",
    "$comment",
    "$id",
    "typeName",
    "sourceUrl",
    "handlers",
    "tagging",
    "taggable",
    "primaryIdentifier",
    "additionalIdentifiers",
    "readOnlyProperties",
    "createOnlyProperties",
    "writeOnlyProperties",
    "conditionalCreateOnlyProperties",
    "deprecatedProperties",
    "replacementStrategy",
    "propertyTransform",
    "resourceLink",
    "examples",
    "default",
];

/// Options for evolving a validator's context and/or schema.
///
/// Used with `Validator::evolve()` to create a new validator with modified
/// context fields. `None` fields keep the parent value unchanged.
///
/// This mirrors Python's `validator.evolve(context=validator.context.evolve(...))` pattern.
#[derive(Default)]
pub struct ContextEvolution {
    /// Override allowed intrinsic functions. `Some(vec)` replaces the current
    /// function list; `None` keeps the existing value.
    pub functions: Option<Vec<String>>,
    /// Override the active regions.
    pub regions: Option<Vec<String>>,
    /// Override the condition state.
    pub condition_state: Option<std::collections::HashMap<String, bool>>,
}

/// JSON Schema validator with registered keyword validators.
pub struct Validator {
    validators: Arc<HashMap<String, KeywordValidator>>,
    root_schema: Arc<serde_json::Value>,
    store: Arc<HashMap<String, serde_json::Value>>,
    /// When `false` (default), apply CloudFormation type coercion rules:
    /// numbers/booleans accepted where strings are expected, numeric strings
    /// accepted where numbers/integers are expected.  When `true`, exact
    /// JSON Schema type matching is enforced.
    pub strict_types: bool,
    /// Optional CloudFormation context for inline function resolution.
    /// When set, `validate_schema` resolves intrinsic functions (Ref, Fn::If,
    /// Fn::Sub, etc.) before running keyword validators.
    pub(crate) context: Option<Arc<Context>>,
    /// CfnLintRule rules dispatched via the synthetic `cfnLint` schema keyword.
    cfn_lint_rules: Option<Arc<KeywordRuleRegistry>>,
    /// Type-based CFN path for keyword rule dispatch (e.g. "Resources/AWS::EC2::Instance/Properties").
    /// Separate from the instance path used in error output.
    cfn_path: Vec<String>,
}

impl Validator {
    /// Create a new validator with all standard keywords registered.
    pub fn new(root_schema: serde_json::Value) -> Self {
        Self::new_with_store(root_schema, HashMap::new())
    }

    /// Create a new validator with a schema store for cross-schema `$ref` resolution.
    ///
    /// The store maps schema names (e.g. `"policy"`) to their JSON Schema values.
    /// Cross-schema refs like `"policy#/definitions/Action"` will be resolved by
    /// looking up the schema name in the store and following the JSON pointer.
    pub fn new_with_store(
        root_schema: serde_json::Value,
        store: HashMap<String, serde_json::Value>,
    ) -> Self {
        use std::sync::LazyLock;
        static DEFAULT_VALIDATORS: LazyLock<Arc<HashMap<String, KeywordValidator>>> =
            LazyLock::new(|| {
                let mut m = HashMap::new();

                // Type
                m.insert(
                    "type".to_string(),
                    keywords::validate_type as KeywordValidator,
                );

                // String
                m.insert(
                    "minLength".to_string(),
                    keywords::validate_min_length as KeywordValidator,
                );
                m.insert(
                    "maxLength".to_string(),
                    keywords::validate_max_length as KeywordValidator,
                );
                m.insert(
                    "pattern".to_string(),
                    keywords::validate_pattern as KeywordValidator,
                );

                // Numeric
                m.insert(
                    "minimum".to_string(),
                    keywords::validate_minimum as KeywordValidator,
                );
                m.insert(
                    "maximum".to_string(),
                    keywords::validate_maximum as KeywordValidator,
                );
                m.insert(
                    "exclusiveMinimum".to_string(),
                    keywords::validate_exclusive_minimum as KeywordValidator,
                );
                m.insert(
                    "exclusiveMaximum".to_string(),
                    keywords::validate_exclusive_maximum as KeywordValidator,
                );
                m.insert(
                    "multipleOf".to_string(),
                    keywords::validate_multiple_of as KeywordValidator,
                );

                // Object
                m.insert(
                    "properties".to_string(),
                    keywords::validate_properties as KeywordValidator,
                );
                m.insert(
                    "required".to_string(),
                    keywords::validate_required as KeywordValidator,
                );
                m.insert(
                    "additionalProperties".to_string(),
                    keywords::validate_additional_properties as KeywordValidator,
                );
                m.insert(
                    "patternProperties".to_string(),
                    keywords::validate_pattern_properties as KeywordValidator,
                );
                m.insert(
                    "dependentRequired".to_string(),
                    keywords::validate_dependent_required as KeywordValidator,
                );
                m.insert(
                    "dependentExcluded".to_string(),
                    keywords::validate_dependent_excluded as KeywordValidator,
                );
                m.insert(
                    "maxProperties".to_string(),
                    keywords::validate_max_properties as KeywordValidator,
                );
                m.insert(
                    "minProperties".to_string(),
                    keywords::validate_min_properties as KeywordValidator,
                );
                m.insert(
                    "propertyNames".to_string(),
                    keywords::validate_property_names as KeywordValidator,
                );
                m.insert(
                    "requiredXor".to_string(),
                    keywords::validate_required_xor as KeywordValidator,
                );
                m.insert(
                    "requiredOr".to_string(),
                    keywords::validate_required_or as KeywordValidator,
                );

                // Array
                m.insert(
                    "items".to_string(),
                    keywords::validate_items as KeywordValidator,
                );
                m.insert(
                    "minItems".to_string(),
                    keywords::validate_min_items as KeywordValidator,
                );
                m.insert(
                    "maxItems".to_string(),
                    keywords::validate_max_items as KeywordValidator,
                );
                m.insert(
                    "maxUniqueItems".to_string(),
                    keywords::validate_max_unique_items as KeywordValidator,
                );
                m.insert(
                    "uniqueItems".to_string(),
                    keywords::validate_unique_items as KeywordValidator,
                );
                m.insert(
                    "contains".to_string(),
                    keywords::validate_contains as KeywordValidator,
                );
                m.insert(
                    "prefixItems".to_string(),
                    keywords::validate_prefix_items as KeywordValidator,
                );
                m.insert(
                    "uniqueKeys".to_string(),
                    keywords::validate_unique_keys as KeywordValidator,
                );

                // Value
                m.insert(
                    "enum".to_string(),
                    keywords::validate_enum as KeywordValidator,
                );
                m.insert(
                    "enumCaseInsensitive".to_string(),
                    keywords::validate_enum_case_insensitive as KeywordValidator,
                );
                m.insert(
                    "const".to_string(),
                    keywords::validate_const as KeywordValidator,
                );

                // Composition
                m.insert(
                    "allOf".to_string(),
                    keywords::validate_all_of as KeywordValidator,
                );
                m.insert(
                    "anyOf".to_string(),
                    keywords::validate_any_of as KeywordValidator,
                );
                m.insert(
                    "oneOf".to_string(),
                    keywords::validate_one_of as KeywordValidator,
                );
                m.insert(
                    "not".to_string(),
                    keywords::validate_not as KeywordValidator,
                );

                // Conditional
                m.insert(
                    "if".to_string(),
                    keywords::validate_if_then_else as KeywordValidator,
                );

                // Format
                m.insert(
                    "format".to_string(),
                    keywords::validate_format as KeywordValidator,
                );

                // CloudFormation function keywords (dispatched by filter)
                m.insert(
                    "ref".to_string(),
                    keywords::validate_ref as KeywordValidator,
                );
                m.insert(
                    "fn_if".to_string(),
                    keywords::validate_fn_if as KeywordValidator,
                );
                m.insert(
                    "fn_sub".to_string(),
                    keywords::validate_fn_sub as KeywordValidator,
                );
                m.insert(
                    "fn_join".to_string(),
                    keywords::validate_fn_resolvable as KeywordValidator,
                );
                m.insert(
                    "fn_select".to_string(),
                    keywords::validate_fn_resolve_and_check as KeywordValidator,
                );
                m.insert(
                    "fn_split".to_string(),
                    keywords::validate_fn_resolvable as KeywordValidator,
                );
                m.insert(
                    "fn_findinmap".to_string(),
                    keywords::validate_fn_resolve_and_check as KeywordValidator,
                );
                m.insert(
                    "fn_base64".to_string(),
                    keywords::validate_fn_resolve_and_check as KeywordValidator,
                );
                m.insert(
                    "fn_getatt".to_string(),
                    keywords::validate_fn_getatt as KeywordValidator,
                );
                m.insert(
                    "fn_getazs".to_string(),
                    keywords::validate_fn_resolve_and_check as KeywordValidator,
                );
                m.insert(
                    "fn_importvalue".to_string(),
                    keywords::validate_fn_resolve_and_check as KeywordValidator,
                );
                m.insert(
                    "fn_transform".to_string(),
                    keywords::validate_fn_unknown as KeywordValidator,
                );
                m.insert(
                    "fn_tojsonstring".to_string(),
                    keywords::validate_fn_resolve_and_check as KeywordValidator,
                );
                m.insert(
                    "fn_length".to_string(),
                    keywords::validate_fn_resolve_and_check as KeywordValidator,
                );
                m.insert(
                    "fn_cidr".to_string(),
                    keywords::validate_fn_resolve_and_check as KeywordValidator,
                );
                m.insert(
                    "fn_getstackoutput".to_string(),
                    keywords::validate_fn_getstackoutput as KeywordValidator,
                );
                m.insert(
                    "fn_equals".to_string(),
                    keywords::validate_fn_structure_only as KeywordValidator,
                );
                m.insert(
                    "fn_condition".to_string(),
                    keywords::validate_fn_structure_only as KeywordValidator,
                );
                m.insert(
                    "fn_unknown".to_string(),
                    keywords::validate_fn_unknown as KeywordValidator,
                );
                m.insert(
                    "dynamicReference".to_string(),
                    keywords::validate_dynamic_reference as KeywordValidator,
                );
                m.insert(
                    "dynamicValidation".to_string(),
                    keywords::validate_dynamic_validation as KeywordValidator,
                );
                m.insert(
                    "cfnLint".to_string(),
                    keywords::validate_cfn_lint as KeywordValidator,
                );
                m.insert(
                    "cfnGather".to_string(),
                    keywords::validate_cfn_gather as KeywordValidator,
                );

                Arc::new(m)
            });

        Validator {
            validators: Arc::clone(&DEFAULT_VALIDATORS),
            root_schema: Arc::new(root_schema),
            store: Arc::new(store),
            strict_types: false,
            context: None,
            cfn_lint_rules: None,
            cfn_path: Vec::new(),
        }
    }

    /// Create a strict-mode validator (exact JSON Schema type matching).
    pub fn new_strict(root_schema: serde_json::Value) -> Self {
        let mut v = Self::new(root_schema);
        v.strict_types = true;
        v
    }

    /// Create a strict-mode validator with a schema store.
    pub fn new_with_store_strict(
        root_schema: serde_json::Value,
        store: HashMap<String, serde_json::Value>,
    ) -> Self {
        let mut v = Self::new_with_store(root_schema, store);
        v.strict_types = true;
        v
    }

    /// Create a validator with a CloudFormation context for inline function resolution.
    pub fn new_with_context(root_schema: serde_json::Value, context: Arc<Context>) -> Self {
        let mut v = Self::new(root_schema);
        v.context = Some(context);
        v
    }

    /// Attach CfnLintRule rules for dispatch via the `cfnLint` schema keyword.
    pub fn set_cfn_lint_rules(&mut self, rules: Arc<KeywordRuleRegistry>) {
        self.cfn_lint_rules = Some(rules);
    }

    /// Clone this validator but without cfnLint keyword rules.
    /// Used by schema-based rules to validate with full context/function handling
    /// but without triggering recursive keyword rule dispatch.
    pub fn without_cfn_lint_rules(&self) -> Self {
        Validator {
            validators: Arc::clone(&self.validators),
            root_schema: self.root_schema.clone(),
            store: self.store.clone(),
            strict_types: self.strict_types,
            context: self.context.clone(),
            cfn_lint_rules: None,
            cfn_path: vec![],
        }
    }

    /// Create a new validator with an evolved context.
    ///
    /// This mirrors Python's `validator.evolve(context=validator.context.evolve(...))`
    /// pattern. Rules use this to create sub-validators with restricted functions,
    /// different regions, or modified condition state, then validate sub-nodes
    /// through the schema engine with those restrictions.
    ///
    /// If no context is set on this validator, the evolution is a no-op (returns
    /// a clone with no context).
    pub fn evolve(&self, options: ContextEvolution) -> Self {
        let new_context = match &self.context {
            Some(ctx) => {
                let mut ctx_opts = crate::context::ContextOptions::default();
                if let Some(functions) = options.functions {
                    ctx_opts.functions = Some(functions);
                }
                if let Some(regions) = options.regions {
                    ctx_opts.regions = Some(regions);
                }
                if let Some(condition_state) = options.condition_state {
                    ctx_opts.condition_state = Some(condition_state);
                }
                Some(Arc::new(ctx.evolve(ctx_opts)))
            }
            None => None,
        };

        Validator {
            validators: Arc::clone(&self.validators),
            root_schema: self.root_schema.clone(),
            store: self.store.clone(),
            strict_types: self.strict_types,
            context: new_context,
            cfn_lint_rules: self.cfn_lint_rules.clone(),
            cfn_path: self.cfn_path.clone(),
        }
    }

    /// Set the type-based CFN path for keyword rule dispatch.
    pub fn set_cfn_path(&mut self, cfn_path: Vec<String>) {
        self.cfn_path = cfn_path;
    }

    /// Access the CfnLintRule rule registry.
    pub fn cfn_lint_rules(&self) -> Option<&KeywordRuleRegistry> {
        self.cfn_lint_rules.as_deref()
    }

    /// Access the CloudFormation context.
    pub fn context(&self) -> Option<&Context> {
        self.context.as_deref()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::*;
    use serde_json::json;

    fn pos() -> Span {
        Span {
            start: Position { line: 1, column: 1 },
            end: Position { line: 1, column: 1 },
        }
    }

    fn str_node(s: &str) -> AstNode {
        AstNode::String(StringNode {
            value: s.to_string(),
            span: pos(),
        })
    }

    fn num_node(n: f64) -> AstNode {
        AstNode::Number(NumberNode {
            value: n,
            span: pos(),
        })
    }

    fn bool_node(b: bool) -> AstNode {
        AstNode::Bool(BoolNode {
            value: b,
            span: pos(),
        })
    }

    fn obj_node(props: Vec<(&str, AstNode)>) -> AstNode {
        let mut map: Vec<ObjectEntry> = Vec::new();
        for (k, v) in props {
            map.push(ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: k.to_string(),
                    span: Span::default(),
                }),
                key: k.to_string(),
                value: v,
                key_span: Span::default(),
            });
        }
        AstNode::Object(ObjectNode {
            entries: map,
            span: pos(),
        })
    }

    fn arr_node(elems: Vec<AstNode>) -> AstNode {
        AstNode::Array(ArrayNode {
            elements: elems,
            span: pos(),
        })
    }

    #[test]
    fn test_type_valid_string() {
        let schema = json!({"type": "string"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&str_node("hello"), &schema, &[]);
        assert!(errs.is_empty());
    }

    #[test]
    fn test_type_invalid() {
        let schema = json!({"type": "string"});
        let v = Validator::new_strict(schema.clone());
        let errs = v.validate(&num_node(42.0), &schema, &[]);
        assert_eq!(errs.len(), 1);
        assert_eq!(errs[0].keyword, "type");
    }

    #[test]
    fn test_type_integer_matches_number() {
        let schema = json!({"type": "number"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&num_node(42.0), &schema, &[]);
        assert!(errs.is_empty());
    }

    #[test]
    fn test_type_array_form() {
        let schema = json!({"type": ["string", "integer"]});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&str_node("hi"), &schema, &[]).is_empty());
        assert!(v.validate(&num_node(5.0), &schema, &[]).is_empty());
        // In relaxed mode, bool coerces to string — use strict for this check
        let v_strict = Validator::new_strict(schema.clone());
        assert!(!v_strict.validate(&bool_node(true), &schema, &[]).is_empty());
    }

    #[test]
    fn test_required() {
        let schema = json!({"type": "object", "required": ["Name"]});
        let v = Validator::new(schema.clone());

        let valid = obj_node(vec![("Name", str_node("test"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![]);
        let errs = v.validate(&invalid, &schema, &[]);
        assert_eq!(errs.len(), 1);
        assert_eq!(errs[0].keyword, "required");
    }

    #[test]
    fn test_enum_valid() {
        let schema = json!({"enum": ["Enabled", "Suspended"]});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&str_node("Enabled"), &schema, &[]).is_empty());
    }

    #[test]
    fn test_enum_invalid() {
        let schema = json!({"enum": ["Enabled", "Suspended"]});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&str_node("Invalid"), &schema, &[]);
        assert_eq!(errs.len(), 1);
        assert_eq!(errs[0].keyword, "enum");
    }

    #[test]
    fn test_pattern_valid() {
        let schema = json!({"pattern": "^[a-z]+$"});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&str_node("abc"), &schema, &[]).is_empty());
    }

    #[test]
    fn test_pattern_invalid() {
        let schema = json!({"pattern": "^[a-z]+$"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&str_node("ABC"), &schema, &[]);
        assert_eq!(errs.len(), 1);
        assert_eq!(errs[0].keyword, "pattern");
    }

    #[test]
    fn test_all_of() {
        let schema = json!({
            "allOf": [
                {"minLength": 2},
                {"maxLength": 5}
            ]
        });
        let v = Validator::new(schema.clone());
        assert!(v.validate(&str_node("abc"), &schema, &[]).is_empty());
        assert!(!v.validate(&str_node("a"), &schema, &[]).is_empty());
    }

    #[test]
    fn test_any_of() {
        let schema = json!({
            "anyOf": [
                {"type": "string"},
                {"type": "number"}
            ]
        });
        let v = Validator::new(schema.clone());
        assert!(v.validate(&str_node("hi"), &schema, &[]).is_empty());
        assert!(v.validate(&num_node(42.0), &schema, &[]).is_empty());
        // In relaxed mode, bool coerces to string — use strict for this check
        let v_strict = Validator::new_strict(schema.clone());
        assert!(!v_strict.validate(&bool_node(true), &schema, &[]).is_empty());
    }

    #[test]
    fn test_one_of() {
        let schema = json!({
            "oneOf": [
                {"type": "string"},
                {"type": "number"}
            ]
        });
        let v = Validator::new_strict(schema.clone());
        assert!(v.validate(&str_node("hi"), &schema, &[]).is_empty());
        assert!(!v.validate(&bool_node(true), &schema, &[]).is_empty());
    }

    #[test]
    fn test_if_then_else() {
        let schema = json!({
            "if": {"type": "string"},
            "then": {"minLength": 3}
        });
        let v = Validator::new_strict(schema.clone());
        // if matches, then applies
        assert!(v.validate(&str_node("abc"), &schema, &[]).is_empty());
        assert!(!v.validate(&str_node("ab"), &schema, &[]).is_empty());
        // if doesn't match, skip then
        assert!(v.validate(&num_node(1.0), &schema, &[]).is_empty());
    }

    #[test]
    fn test_if_then_else_with_else() {
        let schema = json!({
            "if": {"type": "string"},
            "then": {"minLength": 3},
            "else": {"minimum": 10}
        });
        let v = Validator::new_strict(schema.clone());
        // if matches → then
        assert!(v.validate(&str_node("abc"), &schema, &[]).is_empty());
        // if doesn't match → else
        assert!(v.validate(&num_node(15.0), &schema, &[]).is_empty());
        assert!(!v.validate(&num_node(5.0), &schema, &[]).is_empty());
    }

    #[test]
    fn test_ref_basic() {
        let schema = json!({
            "definitions": {
                "Name": {"type": "string"}
            },
            "properties": {
                "Name": {"$ref": "#/definitions/Name"}
            }
        });
        let v = Validator::new(schema.clone());
        let obj = obj_node(vec![("Name", str_node("hello"))]);
        assert!(v.validate(&obj, &schema, &[]).is_empty());
    }

    #[test]
    fn test_ref_type_mismatch() {
        let schema = json!({
            "definitions": {
                "Name": {"type": "string"}
            },
            "properties": {
                "Name": {"$ref": "#/definitions/Name"}
            }
        });
        let v = Validator::new_strict(schema.clone());
        let obj = obj_node(vec![("Name", num_node(42.0))]);
        let errs = v.validate(&obj, &schema, &[]);
        assert!(!errs.is_empty());
        assert_eq!(errs[0].keyword, "type");
    }

    #[test]
    fn test_ref_not_found() {
        let schema = json!({
            "properties": {
                "Name": {"$ref": "#/definitions/DoesNotExist"}
            }
        });
        let v = Validator::new(schema.clone());
        let obj = obj_node(vec![("Name", str_node("anything"))]);
        let errs = v.validate(&obj, &schema, &[]);
        assert!(!errs.is_empty());
        assert_eq!(errs[0].keyword, "$ref");
    }

    #[test]
    fn test_ref_nested() {
        let schema = json!({
            "definitions": {
                "Inner": {"type": "string"},
                "Outer": {"$ref": "#/definitions/Inner"}
            },
            "properties": {
                "Value": {"$ref": "#/definitions/Outer"}
            }
        });
        let v = Validator::new_strict(schema.clone());
        let valid = obj_node(vec![("Value", str_node("ok"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("Value", bool_node(true))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_ref_with_constraints() {
        let schema = json!({
            "definitions": {
                "Tag": {"type": "string", "maxLength": 5}
            },
            "properties": {
                "Tag": {"$ref": "#/definitions/Tag"}
            }
        });
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("Tag", str_node("ok"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("Tag", str_node("toolong"))]);
        let errs = v.validate(&invalid, &schema, &[]);
        assert!(errs.iter().any(|e| e.keyword == "maxLength"));
    }

    #[test]
    fn test_additional_properties_false() {
        let schema = json!({
            "properties": {
                "Name": {"type": "string"}
            },
            "additionalProperties": false
        });
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("Name", str_node("test"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("Name", str_node("test")), ("Extra", str_node("bad"))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_additional_properties_schema() {
        let schema = json!({
            "properties": {
                "Name": {"type": "string"}
            },
            "additionalProperties": {"type": "integer"}
        });
        let v = Validator::new(schema.clone());
        // additional prop matches schema
        let valid = obj_node(vec![("Name", str_node("test")), ("Count", num_node(5.0))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        // additional prop doesn't match schema
        let invalid = obj_node(vec![("Name", str_node("test")), ("Count", str_node("bad"))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_items() {
        let schema = json!({
            "type": "array",
            "items": {"type": "string"}
        });
        let v = Validator::new_strict(schema.clone());
        let valid = arr_node(vec![str_node("a"), str_node("b")]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = arr_node(vec![str_node("a"), num_node(42.0)]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_min_max_items() {
        let schema = json!({"minItems": 2, "maxItems": 3});
        let v = Validator::new(schema.clone());
        let valid = arr_node(vec![str_node("a"), str_node("b")]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let too_few = arr_node(vec![str_node("a")]);
        assert!(!v.validate(&too_few, &schema, &[]).is_empty());

        let too_many = arr_node(vec![
            str_node("a"),
            str_node("b"),
            str_node("c"),
            str_node("d"),
        ]);
        assert!(!v.validate(&too_many, &schema, &[]).is_empty());
    }

    #[test]
    fn test_unique_items() {
        let schema = json!({"uniqueItems": true});
        let v = Validator::new(schema.clone());
        let valid = arr_node(vec![str_node("a"), str_node("b")]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = arr_node(vec![str_node("a"), str_node("a")]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_min_max_length() {
        let schema = json!({"minLength": 2, "maxLength": 5});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&str_node("abc"), &schema, &[]).is_empty());
        assert!(!v.validate(&str_node("a"), &schema, &[]).is_empty());
        assert!(!v.validate(&str_node("toolong"), &schema, &[]).is_empty());
    }

    #[test]
    fn test_minimum_maximum() {
        let schema = json!({"minimum": 1, "maximum": 10});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&num_node(5.0), &schema, &[]).is_empty());
        assert!(!v.validate(&num_node(0.0), &schema, &[]).is_empty());
        assert!(!v.validate(&num_node(11.0), &schema, &[]).is_empty());
    }

    #[test]
    fn test_exclusive_min_max() {
        let schema = json!({"exclusiveMinimum": 1, "exclusiveMaximum": 10});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&num_node(5.0), &schema, &[]).is_empty());
        assert!(!v.validate(&num_node(1.0), &schema, &[]).is_empty());
        assert!(!v.validate(&num_node(10.0), &schema, &[]).is_empty());
    }

    #[test]
    fn test_const() {
        let schema = json!({"const": "exact"});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&str_node("exact"), &schema, &[]).is_empty());
        assert!(!v.validate(&str_node("other"), &schema, &[]).is_empty());
    }

    #[test]
    fn test_not() {
        let schema = json!({"not": {"type": "string"}});
        let v = Validator::new_strict(schema.clone());
        assert!(v.validate(&num_node(42.0), &schema, &[]).is_empty());
        assert!(!v.validate(&str_node("hello"), &schema, &[]).is_empty());
    }

    #[test]
    fn test_dependent_required() {
        let schema = json!({
            "dependentRequired": {
                "A": ["B"]
            }
        });
        let v = Validator::new(schema.clone());

        let satisfied = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
        assert!(v.validate(&satisfied, &schema, &[]).is_empty());

        let missing = obj_node(vec![("A", str_node("1"))]);
        assert!(!v.validate(&missing, &schema, &[]).is_empty());

        // trigger absent → no check
        let no_trigger = obj_node(vec![("C", str_node("1"))]);
        assert!(v.validate(&no_trigger, &schema, &[]).is_empty());
    }

    #[test]
    fn test_pattern_properties() {
        let schema = json!({
            "patternProperties": {
                "^x-": {"type": "string"}
            }
        });
        let v = Validator::new_strict(schema.clone());
        let valid = obj_node(vec![("x-custom", str_node("ok"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("x-custom", num_node(42.0))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_properties_nested_validation() {
        let schema = json!({
            "properties": {
                "name": {"type": "string", "minLength": 2},
                "age": {"type": "integer", "minimum": 0}
            }
        });
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("name", str_node("Jo")), ("age", num_node(25.0))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("name", str_node("J"))]);
        let errs = v.validate(&invalid, &schema, &[]);
        assert!(errs.iter().any(|e| e.keyword == "minLength"));
    }

    #[test]
    fn test_skip_non_validation_keywords() {
        let schema = json!({
            "type": "string",
            "description": "A name field",
            "title": "Name",
            "default": "unnamed",
            "examples": ["foo"],
            "$comment": "internal note"
        });
        let v = Validator::new(schema.clone());
        // Should only validate "type", skip the rest
        assert!(v.validate(&str_node("hello"), &schema, &[]).is_empty());
    }

    #[test]
    fn test_additional_properties_with_pattern_properties() {
        let schema = json!({
            "properties": {
                "Name": {"type": "string"}
            },
            "patternProperties": {
                "^x-": {"type": "string"}
            },
            "additionalProperties": false
        });
        let v = Validator::new(schema.clone());
        // x-custom matches patternProperties, should be allowed
        let valid = obj_node(vec![
            ("Name", str_node("test")),
            ("x-custom", str_node("ok")),
        ]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        // unknown doesn't match either
        let invalid = obj_node(vec![
            ("Name", str_node("test")),
            ("unknown", str_node("bad")),
        ]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_pattern_properties_fancy_regex_cached() {
        // A negative lookahead requires the fancy_regex fallback: the standard
        // `regex` engine rejects look-around, so this exercises the cached
        // fancy path in `compile_pattern`.
        let schema = json!({
            "patternProperties": {
                "^(?!aws:).+$": {"type": "string"}
            }
        });
        let v = Validator::new_strict(schema.clone());

        // "custom" does not start with "aws:" → matches → value must be a string.
        let valid = obj_node(vec![("custom", str_node("ok"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("custom", num_node(42.0))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
        // Re-validate to confirm the cached compiled pattern behaves identically.
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_additional_properties_fancy_regex_cached() {
        // additionalProperties gating on a fancy-regex patternProperties key,
        // routed through the shared compiled-pattern cache.
        let schema = json!({
            "properties": {
                "Name": {"type": "string"}
            },
            "patternProperties": {
                "^(?!aws:).+$": {}
            },
            "additionalProperties": false
        });
        let v = Validator::new(schema.clone());

        // "custom" matches the lookahead pattern → permitted as additional.
        let valid = obj_node(vec![("Name", str_node("t")), ("custom", str_node("ok"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        // "aws:internal" fails the negative lookahead → unmatched → not allowed.
        let invalid = obj_node(vec![
            ("Name", str_node("t")),
            ("aws:internal", str_node("bad")),
        ]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    // ===== Integration tests for new keywords =====

    #[test]
    fn test_dependent_excluded_integration() {
        let schema = json!({"dependentExcluded": {"A": ["B"]}});
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("A", str_node("1")), ("C", str_node("2"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_max_properties_integration() {
        let schema = json!({"maxProperties": 1});
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("A", str_node("1"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_min_properties_integration() {
        let schema = json!({"minProperties": 2});
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("A", str_node("1"))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_property_names_integration() {
        let schema = json!({"propertyNames": {"pattern": "^[a-z]+$"}});
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("abc", str_node("1"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = obj_node(vec![("ABC", str_node("1"))]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_contains_integration() {
        let schema = json!({"contains": {"type": "string"}});
        let v = Validator::new_strict(schema.clone());
        let valid = arr_node(vec![num_node(1.0), str_node("ok")]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = arr_node(vec![num_node(1.0), num_node(2.0)]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_prefix_items_integration() {
        let schema = json!({"prefixItems": [{"type": "string"}, {"type": "integer"}]});
        let v = Validator::new_strict(schema.clone());
        let valid = arr_node(vec![str_node("a"), num_node(1.0)]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = arr_node(vec![num_node(1.0), str_node("b")]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_unique_keys_integration() {
        let schema = json!({"uniqueKeys": ["Name"]});
        let v = Validator::new(schema.clone());
        let valid = arr_node(vec![
            obj_node(vec![("Name", str_node("a"))]),
            obj_node(vec![("Name", str_node("b"))]),
        ]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let invalid = arr_node(vec![
            obj_node(vec![("Name", str_node("a"))]),
            obj_node(vec![("Name", str_node("a"))]),
        ]);
        assert!(!v.validate(&invalid, &schema, &[]).is_empty());
    }

    #[test]
    fn test_multiple_of_integration() {
        let schema = json!({"multipleOf": 3});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&num_node(9.0), &schema, &[]).is_empty());
        assert!(!v.validate(&num_node(10.0), &schema, &[]).is_empty());
    }

    #[test]
    fn test_required_xor_integration() {
        let schema = json!({"requiredXor": ["A", "B"]});
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("A", str_node("1"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let both = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
        assert!(!v.validate(&both, &schema, &[]).is_empty());

        let neither = obj_node(vec![("C", str_node("1"))]);
        assert!(!v.validate(&neither, &schema, &[]).is_empty());
    }

    #[test]
    fn test_required_or_integration() {
        let schema = json!({"requiredOr": ["A", "B"]});
        let v = Validator::new(schema.clone());
        let valid = obj_node(vec![("A", str_node("1"))]);
        assert!(v.validate(&valid, &schema, &[]).is_empty());

        let both = obj_node(vec![("A", str_node("1")), ("B", str_node("2"))]);
        assert!(v.validate(&both, &schema, &[]).is_empty());

        let neither = obj_node(vec![("C", str_node("1"))]);
        assert!(!v.validate(&neither, &schema, &[]).is_empty());
    }

    #[test]
    fn test_enum_case_insensitive_integration() {
        let schema = json!({"enumCaseInsensitive": ["Enabled", "Disabled"]});
        let v = Validator::new(schema.clone());
        assert!(v.validate(&str_node("enabled"), &schema, &[]).is_empty());
        assert!(v.validate(&str_node("ENABLED"), &schema, &[]).is_empty());
        assert!(!v.validate(&str_node("Unknown"), &schema, &[]).is_empty());
    }

    #[test]
    fn test_cross_schema_ref() {
        let other_schema = json!({
            "definitions": {
                "Foo": {
                    "type": "string",
                    "enum": ["bar", "baz"]
                }
            }
        });
        let root_schema = json!({
            "properties": {
                "Name": {"$ref": "other#/definitions/Foo"}
            }
        });
        let mut store = HashMap::new();
        store.insert("other".to_string(), other_schema);
        let v = Validator::new_with_store(root_schema.clone(), store);

        let valid = obj_node(vec![("Name", str_node("bar"))]);
        assert!(v.validate(&valid, &root_schema, &[]).is_empty());

        let invalid = obj_node(vec![("Name", str_node("nope"))]);
        let errs = v.validate(&invalid, &root_schema, &[]);
        assert!(!errs.is_empty());
        assert!(errs.iter().any(|e| e.keyword == "enum"));
    }

    #[test]
    fn test_cross_schema_ref_not_found() {
        let root_schema = json!({
            "properties": {
                "Name": {"$ref": "missing#/definitions/Foo"}
            }
        });
        let v = Validator::new(root_schema.clone());
        let obj = obj_node(vec![("Name", str_node("anything"))]);
        let errs = v.validate(&obj, &root_schema, &[]);
        assert!(!errs.is_empty());
        assert_eq!(errs[0].keyword, "$ref");
    }

    // ===== strict_types tests =====

    #[test]
    fn test_relaxed_number_where_string_expected_passes() {
        let schema = json!({"type": "string"});
        let v = Validator::new(schema.clone());
        assert!(!v.strict_types);
        let errs = v.validate(&num_node(42.0), &schema, &[]);
        assert!(
            errs.is_empty(),
            "Relaxed mode: number should coerce to string"
        );
    }

    #[test]
    fn test_relaxed_boolean_where_string_expected_passes() {
        let schema = json!({"type": "string"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&bool_node(true), &schema, &[]);
        assert!(
            errs.is_empty(),
            "Relaxed mode: boolean should coerce to string"
        );
    }

    #[test]
    fn test_relaxed_object_where_string_expected_fails() {
        let schema = json!({"type": "string"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&obj_node(vec![]), &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Relaxed mode: object should NOT coerce to string"
        );
    }

    #[test]
    fn test_relaxed_array_where_string_expected_fails() {
        let schema = json!({"type": "string"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&arr_node(vec![]), &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Relaxed mode: array should NOT coerce to string"
        );
    }

    #[test]
    fn test_relaxed_numeric_string_where_number_expected_passes() {
        let schema = json!({"type": "number"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&str_node("10"), &schema, &[]);
        assert!(
            errs.is_empty(),
            "Relaxed mode: string '10' should coerce to number"
        );
    }

    #[test]
    fn test_relaxed_numeric_string_where_integer_expected_passes() {
        let schema = json!({"type": "integer"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&str_node("42"), &schema, &[]);
        assert!(
            errs.is_empty(),
            "Relaxed mode: string '42' should coerce to integer"
        );
    }

    #[test]
    fn test_relaxed_float_string_where_integer_expected_fails() {
        let schema = json!({"type": "integer"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&str_node("3.14"), &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Relaxed mode: string '3.14' should NOT coerce to integer"
        );
    }

    #[test]
    fn test_relaxed_non_numeric_string_where_number_expected_fails() {
        let schema = json!({"type": "number"});
        let v = Validator::new(schema.clone());
        let errs = v.validate(&str_node("hello"), &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Relaxed mode: non-numeric string should NOT coerce to number"
        );
    }

    #[test]
    fn test_strict_number_where_string_expected_fails() {
        let schema = json!({"type": "string"});
        let v = Validator::new_strict(schema.clone());
        assert!(v.strict_types);
        let errs = v.validate(&num_node(42.0), &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Strict mode: number should NOT pass for string"
        );
    }

    #[test]
    fn test_strict_boolean_where_string_expected_fails() {
        let schema = json!({"type": "string"});
        let v = Validator::new_strict(schema.clone());
        let errs = v.validate(&bool_node(true), &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Strict mode: boolean should NOT pass for string"
        );
    }

    #[test]
    fn test_strict_string_where_number_expected_fails() {
        let schema = json!({"type": "number"});
        let v = Validator::new_strict(schema.clone());
        let errs = v.validate(&str_node("10"), &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Strict mode: string should NOT pass for number"
        );
    }

    #[test]
    fn test_strict_string_where_integer_expected_fails() {
        let schema = json!({"type": "integer"});
        let v = Validator::new_strict(schema.clone());
        let errs = v.validate(&str_node("42"), &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Strict mode: string should NOT pass for integer"
        );
    }

    #[test]
    fn test_strict_exact_types_still_pass() {
        let v = Validator::new_strict(json!({}));
        assert!(v
            .validate(&str_node("hi"), &json!({"type": "string"}), &[])
            .is_empty());
        assert!(v
            .validate(&num_node(42.0), &json!({"type": "integer"}), &[])
            .is_empty());
        assert!(v
            .validate(&num_node(3.5), &json!({"type": "number"}), &[])
            .is_empty());
        assert!(v
            .validate(&bool_node(true), &json!({"type": "boolean"}), &[])
            .is_empty());
    }

    #[test]
    fn test_relaxed_null_where_string_expected_fails() {
        let schema = json!({"type": "string"});
        let v = Validator::new(schema.clone());
        let null_node = AstNode::Null(crate::ast::NullNode { span: pos() });
        let errs = v.validate(&null_node, &schema, &[]);
        assert!(
            !errs.is_empty(),
            "Relaxed mode: null should NOT coerce to string"
        );
    }

    // ===== evolve() tests =====

    #[test]
    fn test_evolve_restricts_functions() {
        use crate::context::Context;
        use crate::parser;
        use crate::template::Template;

        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = std::sync::Arc::new(Template::from_ast(&ast).unwrap());
        let ctx = Context::new(tmpl);
        let mut v = Validator::new(json!({}));
        v.context = Some(std::sync::Arc::new(ctx));

        // Evolve to only allow Ref and Fn::Sub
        let evolved = v.evolve(ContextEvolution {
            functions: Some(vec!["Ref".to_string(), "Fn::Sub".to_string()]),
            ..Default::default()
        });

        // Check evolved context has restricted functions
        let evolved_ctx = evolved.context().unwrap();
        assert_eq!(
            evolved_ctx.functions,
            Some(vec!["Ref".to_string(), "Fn::Sub".to_string()])
        );
        // Original is unchanged
        let orig_ctx = v.context().unwrap();
        assert_eq!(orig_ctx.functions, None);
    }

    #[test]
    fn test_evolve_changes_regions() {
        use crate::context::Context;
        use crate::parser;
        use crate::template::Template;

        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = std::sync::Arc::new(Template::from_ast(&ast).unwrap());
        let ctx = Context::new(tmpl);
        let mut v = Validator::new(json!({}));
        v.context = Some(std::sync::Arc::new(ctx));

        let evolved = v.evolve(ContextEvolution {
            regions: Some(vec!["eu-west-1".to_string(), "eu-west-2".to_string()]),
            ..Default::default()
        });

        let evolved_ctx = evolved.context().unwrap();
        assert_eq!(evolved_ctx.regions, vec!["eu-west-1", "eu-west-2"]);
        // Original is unchanged
        let orig_ctx = v.context().unwrap();
        assert_eq!(orig_ctx.regions, vec!["us-east-1"]);
    }

    #[test]
    fn test_evolve_without_context_is_noop() {
        let v = Validator::new(json!({}));
        assert!(v.context().is_none());

        let evolved = v.evolve(ContextEvolution {
            functions: Some(vec!["Ref".to_string()]),
            ..Default::default()
        });

        assert!(evolved.context().is_none());
    }

    #[test]
    fn test_evolve_preserves_cfn_lint_rules() {
        use crate::context::Context;
        use crate::jsonschema::cfn_lint_keyword::KeywordRuleRegistry;
        use crate::parser;
        use crate::template::Template;

        let yaml = b"AWSTemplateFormatVersion: '2010-09-09'\n";
        let ast = parser::parse(yaml).unwrap();
        let tmpl = std::sync::Arc::new(Template::from_ast(&ast).unwrap());
        let ctx = Context::new(tmpl);
        let mut v = Validator::new(json!({}));
        v.context = Some(std::sync::Arc::new(ctx));
        let registry = std::sync::Arc::new(KeywordRuleRegistry::new());
        v.set_cfn_lint_rules(registry);

        let evolved = v.evolve(ContextEvolution::default());
        // cfn_lint_rules should still be present
        assert!(evolved.cfn_lint_rules().is_some());
    }
}
