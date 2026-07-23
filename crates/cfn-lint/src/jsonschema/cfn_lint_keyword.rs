use super::{ValidationError, Validator};
use crate::ast::AstNode;
use crate::rules::Severity;
use crate::template::Template;
use std::collections::HashMap;
use std::sync::Arc;

/// Unified trait for all cfn-lint rules.
///
/// Rules declare which CFN paths they handle via `keywords()` (e.g.
/// `"Resources/AWS::EC2::Instance/Properties"`). The validator dispatches
/// to matching rules when it encounters the synthetic `cfnLint` keyword
/// injected by the filter.
///
/// Rules that operate on the full template tree implement `validate_template()`
/// (which receives the template and root AST node). Rules that operate on
/// individual nodes during schema traversal implement `validate()`.
///
/// `short_description()`, `description()`, and `severity()` have defaults so
/// rules that don't need metadata (like extension schema rules) can omit them.
pub trait CfnLintRule: Send + Sync {
    fn id(&self) -> &str;
    fn short_description(&self) -> &str {
        ""
    }
    fn description(&self) -> &str {
        self.short_description()
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }
    fn keywords(&self) -> &[&str];
    /// When true (default), yield all validation errors with their original messages.
    /// When false, pick the best match and replace its message with short_description.
    fn all_matches(&self) -> bool {
        true
    }
    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        _instance: &AstNode,
        _schema: &serde_json::Value,
        _path: &[String],
    ) -> Vec<ValidationError> {
        vec![]
    }
    /// Template-level validation dispatched by the engine for rules with keyword `"/"`.
    /// Rules that need access to the full template tree implement this method.
    fn validate_template(
        &self,
        _template: &Template,
        _root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

// Collect static references to CfnLintRule implementors via inventory.
inventory::collect!(&'static dyn CfnLintRule);

/// Registry mapping CFN paths to keyword rules.
/// Rules are indexed by their first path segment for O(1) bucket lookup on dispatch.
pub struct KeywordRuleRegistry {
    static_rules: Vec<&'static dyn CfnLintRule>,
    dynamic_rules: Vec<Arc<dyn CfnLintRule>>,
    static_index: HashMap<String, Vec<usize>>,
    dynamic_index: HashMap<String, Vec<usize>>,
    static_wildcard: Vec<usize>,
    dynamic_wildcard: Vec<usize>,
}

fn first_segment(keyword: &str) -> &str {
    keyword.split('/').next().unwrap_or("")
}

impl Default for KeywordRuleRegistry {
    fn default() -> Self {
        Self::new()
    }
}

impl KeywordRuleRegistry {
    pub fn new() -> Self {
        Self {
            static_rules: Vec::new(),
            dynamic_rules: Vec::new(),
            static_index: HashMap::new(),
            dynamic_index: HashMap::new(),
            static_wildcard: Vec::new(),
            dynamic_wildcard: Vec::new(),
        }
    }

    /// Build a registry pre-populated from all inventory-registered rules.
    pub fn from_inventory() -> Self {
        let static_rules: Vec<&'static dyn CfnLintRule> =
            inventory::iter::<&'static dyn CfnLintRule>
                .into_iter()
                .copied()
                .collect();
        let mut static_index: HashMap<String, Vec<usize>> = HashMap::new();
        let mut static_wildcard: Vec<usize> = Vec::new();
        for (i, rule) in static_rules.iter().enumerate() {
            let mut indexed_segments: Vec<String> = Vec::new();
            let mut is_wildcard = false;
            for kw in rule.keywords() {
                if *kw == "/" || kw.is_empty() {
                    continue;
                }
                let seg = first_segment(kw);
                if seg == "*" {
                    is_wildcard = true;
                    break;
                } else {
                    let seg_str = seg.to_string();
                    if !indexed_segments.contains(&seg_str) {
                        indexed_segments.push(seg_str.clone());
                        static_index.entry(seg_str).or_default().push(i);
                    }
                }
            }
            if is_wildcard {
                static_wildcard.push(i);
            }
        }
        Self {
            static_rules,
            dynamic_rules: Vec::new(),
            static_index,
            dynamic_index: HashMap::new(),
            static_wildcard,
            dynamic_wildcard: Vec::new(),
        }
    }

    /// Register a static (compile-time) rule reference.
    pub fn register_static(&mut self, rule: &'static dyn CfnLintRule) {
        let idx = self.static_rules.len();
        self.static_rules.push(rule);
        let mut indexed_segments: Vec<String> = Vec::new();
        for kw in rule.keywords() {
            if *kw == "/" || kw.is_empty() {
                continue;
            }
            let seg = first_segment(kw);
            if seg == "*" {
                self.static_wildcard.push(idx);
                break;
            } else {
                let seg_str = seg.to_string();
                if !indexed_segments.contains(&seg_str) {
                    indexed_segments.push(seg_str.clone());
                    self.static_index.entry(seg_str).or_default().push(idx);
                }
            }
        }
    }

    /// Register a dynamic (runtime) CfnLintRule via Arc.
    pub fn register(&mut self, rule: Arc<dyn CfnLintRule>) {
        let idx = self.dynamic_rules.len();
        let mut indexed_segments: Vec<String> = Vec::new();
        for kw in rule.keywords() {
            if *kw == "/" || kw.is_empty() {
                continue;
            }
            let seg = first_segment(kw);
            if seg == "*" {
                self.dynamic_wildcard.push(idx);
                break;
            } else {
                let seg_str = seg.to_string();
                if !indexed_segments.contains(&seg_str) {
                    indexed_segments.push(seg_str.clone());
                    self.dynamic_index.entry(seg_str).or_default().push(idx);
                }
            }
        }
        self.dynamic_rules.push(rule);
    }

    /// Return all CfnLintRule rules (static + dynamic) for template-level dispatch.
    pub fn all_rules(&self) -> Vec<&dyn CfnLintRule> {
        let mut rules: Vec<&dyn CfnLintRule> = Vec::new();
        for r in &self.static_rules {
            rules.push(*r);
        }
        for r in &self.dynamic_rules {
            rules.push(r.as_ref());
        }
        rules
    }

    /// Filter rules by include/exclude prefixes (for rule configuration).
    pub fn filter(&self, include: &[String], exclude: &[String]) -> Vec<&dyn CfnLintRule> {
        self.all_rules()
            .into_iter()
            .filter(|r| {
                (include.is_empty() || include.iter().any(|i| r.id().starts_with(i)))
                    && !exclude.iter().any(|e| r.id().starts_with(e))
            })
            .collect()
    }

    /// Dispatch: find all rules whose keywords match the given path and call them.
    pub fn dispatch(
        &self,
        validator: &Validator,
        path_keyword: &str,
        instance: &AstNode,
        schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let mut errors = Vec::new();
        let seg = first_segment(path_keyword);

        let static_candidates = self
            .static_index
            .get(seg)
            .into_iter()
            .flatten()
            .chain(self.static_wildcard.iter());
        for &idx in static_candidates {
            let rule = self.static_rules[idx];
            for kw in rule.keywords() {
                if keyword_matches(kw, path_keyword) {
                    let mut rule_errors =
                        rule.validate(validator, path_keyword, instance, schema, path);
                    for err in &mut rule_errors {
                        if err.rule_id.is_none() {
                            err.rule_id = Some(rule.id().to_string());
                        }
                        if err.keyword.is_empty() {
                            err.keyword = format!("cfnLint:{}", rule.id());
                        }
                    }
                    errors.extend(rule_errors);
                    break;
                }
            }
        }

        let dynamic_candidates = self
            .dynamic_index
            .get(seg)
            .into_iter()
            .flatten()
            .chain(self.dynamic_wildcard.iter());
        for &idx in dynamic_candidates {
            let rule = self.dynamic_rules[idx].as_ref();
            for kw in rule.keywords() {
                if keyword_matches(kw, path_keyword) {
                    let mut rule_errors =
                        rule.validate(validator, path_keyword, instance, schema, path);
                    for err in &mut rule_errors {
                        if err.rule_id.is_none() {
                            err.rule_id = Some(rule.id().to_string());
                        }
                        if err.keyword.is_empty() {
                            err.keyword = format!("cfnLint:{}", rule.id());
                        }
                    }
                    errors.extend(rule_errors);
                    break;
                }
            }
        }

        errors
    }

    /// Dispatch template-level validation on all CfnLintRule rules.
    /// Called by the engine to run `validate_template()` on every registered rule.
    pub fn validate_template_all(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<ValidationError> {
        let mut issues = Vec::new();
        for rule in &self.static_rules {
            issues.extend(rule.validate_template(template, root));
        }
        for rule in &self.dynamic_rules {
            issues.extend(rule.validate_template(template, root));
        }
        issues
    }
}

/// Match a keyword pattern against a path, where `*` in the pattern
/// matches any single path segment (parameter name, resource name,
/// or numeric array index).
fn keyword_matches(pattern: &str, path: &str) -> bool {
    if pattern == path {
        return true;
    }
    let pat_parts: Vec<&str> = pattern.split('/').collect();
    let path_parts: Vec<&str> = path.split('/').collect();
    if pat_parts.len() != path_parts.len() {
        return false;
    }
    pat_parts
        .iter()
        .zip(path_parts.iter())
        .all(|(p, v)| *p == *v || *p == "*")
}
