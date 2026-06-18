use std::path::PathBuf;
use std::sync::Arc;

pub(crate) mod extensions;
pub(crate) mod fn_if;
pub(crate) mod helpers;
pub(crate) mod rule_mapping;
#[cfg(test)]
mod schema_validation;

pub(crate) use rule_mapping::*;
pub(crate) use helpers::*;
pub(crate) use fn_if::*;
pub(crate) use extensions::*;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::KeywordRuleRegistry;
use crate::jsonschema::ValidationError;
use crate::template::Template;

pub struct Engine {
    schema_provider: Option<Arc<dyn cfn_schema::SchemaProvider>>,
    /// Data directory for rule-specific schemas (IAM, SSM, Step Functions, extensions).
    data_dir: Option<PathBuf>,
    /// Unified rule registry: CfnLintRule implementations dispatched through
    /// the jsonschema validator (keyword dispatch) and template-level validation.
    pub keyword_rules: Arc<KeywordRuleRegistry>,
    /// When true, force strict type checking (E3012) regardless of template metadata.
    pub strict_types: bool,
}

impl Default for Engine {
    fn default() -> Self {
        Self::new()
    }
}


impl Engine {
    pub fn new() -> Self {
        // Keyword rules are auto-registered via inventory at compile time.
        // Rules that require runtime initialization are registered dynamically.
        let mut keyword_rules = KeywordRuleRegistry::from_inventory();
        keyword_rules.register(Arc::new(crate::rules::e2531::E2531::new()));
        keyword_rules.register(Arc::new(crate::rules::e2533::E2533::new()));
        keyword_rules.register(Arc::new(crate::rules::w2531::W2531::new()));

        Engine {
            schema_provider: None,
            data_dir: None,
            keyword_rules: Arc::new(keyword_rules),
            strict_types: false,
        }
    }

    /// Create an engine with schema validation enabled.
    /// Falls back to rules-only mode if schemas can't be loaded.
    pub fn with_data_dir(data_dir: PathBuf) -> Self {
        let mut engine = Self::new();
        if let Some(provider) = cfn_schema::BundledSchemaProvider::new(data_dir.clone()) {
            engine.schema_provider = Some(Arc::new(provider));
        }
        engine.data_dir = Some(data_dir);
        engine
    }

    /// Create an engine with an external SchemaProvider (e.g. from cfn-lsp).
    pub fn with_schema_provider(provider: Arc<dyn cfn_schema::SchemaProvider>, data_dir: Option<PathBuf>) -> Self {
        let mut engine = Self::new();
        engine.schema_provider = Some(provider);
        engine.data_dir = data_dir;
        engine
    }

    /// Register additional rules (e.g. custom rules loaded from a file).
    pub fn register_custom_rules(&mut self, rules: Vec<Arc<dyn crate::jsonschema::cfn_lint_keyword::CfnLintRule>>) {
        let keyword_rules = Arc::get_mut(&mut self.keyword_rules)
            .expect("register_custom_rules must be called before validate");
        for rule in rules {
            keyword_rules.register(rule);
        }
    }

    pub fn validate(
        &mut self,
        template: &Template,
        root: &AstNode,
        regions: &[String],
    ) -> Vec<ValidationError> {
        // E1002: Check template file size limit (1MB)
        let mut issues = Vec::new();
        const MAX_TEMPLATE_SIZE: u64 = 1_000_000;
        if let Some(ref filename) = template.filename {
            if let Ok(meta) = std::fs::metadata(filename) {
                if meta.len() > MAX_TEMPLATE_SIZE {
                    issues.push(ValidationError {
                        rule_id: Some("E1002".to_string()),
                        message: format!(
                            "The template file size ({} bytes) exceeds the limit ({} bytes)",
                            meta.len(),
                            MAX_TEMPLATE_SIZE
                        ),
                        path: vec![],
                        span: root.span(),
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
});
                }
            }
        }

        let walker = crate::walker::TemplateWalker::new(
            Arc::clone(&self.keyword_rules),
            self.schema_provider.clone(),
            self.strict_types,
        );
        issues.extend(walker.walk(template, root, regions));

        // Filter out issues suppressed by metadata directives
        let template_ignores = get_ignored_rules(root);
        issues.retain(|issue| {
            let rid = match &issue.rule_id {
                Some(r) => r.as_str(),
                None => return true,
            };
            // Check template-level suppression
            if template_ignores
                .iter()
                .any(|id| rid.starts_with(id))
            {
                return false;
            }
            // Check resource-level suppression
            if issue.path.len() >= 2 && issue.path[0] == "Resources" {
                let resource_name = &issue.path[1];
                if let Some(resource_node) =
                    root.get("Resources").and_then(|r| r.get(resource_name))
                {
                    let resource_ignores = get_ignored_rules(resource_node);
                    if resource_ignores
                        .iter()
                        .any(|id| rid.starts_with(id))
                    {
                        return false;
                    }
                }
            }
            true
        });

        // Suppress E3012 type errors when a function structure error exists at the same path
        // (e.g., E1019 for invalid Sub structure should suppress E3012 type mismatch)
        let fn_error_paths: std::collections::HashSet<Vec<String>> = issues.iter()
            .filter(|i| matches!(i.rule_id.as_deref(), Some("E1019") | Some("E1021") | Some("E1022") | Some("E1017") | Some("E1018")))
            .map(|i| i.path.clone())
            .collect();
        if !fn_error_paths.is_empty() {
            issues.retain(|i| i.rule_id.as_deref() != Some("E3012") || !fn_error_paths.contains(&i.path));
        }

        // Suppress W1020 (Sub not needed) when W1031 (Sub resolved error) fires at the same span.
        // Python's W1020 is a child rule of E1019 that only fires when resolution succeeds.
        let w1031_spans: std::collections::HashSet<(u32, u32)> = issues.iter()
            .filter(|i| i.rule_id.as_deref() == Some("W1031"))
            .map(|i| (i.span.start.line, i.span.start.column))
            .collect();
        if !w1031_spans.is_empty() {
            issues.retain(|i| i.rule_id.as_deref() != Some("W1020") || !w1031_spans.contains(&(i.span.start.line, i.span.start.column)));
        }

        // Deduplicate (same rule can fire from keyword rules AND extension schemas)
        issues.sort_by(|a, b| a.rule_id.cmp(&b.rule_id).then(a.span.start.line.cmp(&b.span.start.line)).then(a.message.cmp(&b.message)));
        issues.dedup_by(|a, b| a.rule_id == b.rule_id && a.path == b.path && a.span == b.span && a.message == b.message);

        // E1019: Deduplicate by (rule_id, span) since standalone rule and pipeline may produce different paths
        {
            let mut seen_e1019 = std::collections::HashSet::new();
            issues.retain(|i| {
                if i.rule_id.as_deref() == Some("E1019") {
                    seen_e1019.insert((i.span.start.line, i.span.start.column, i.message.clone()))
                } else {
                    true
                }
            });
        }


        issues
    }
}



#[cfg(test)]
mod tests;
