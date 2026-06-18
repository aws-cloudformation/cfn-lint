use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::Arc;

use cfn_ast::parser;
use cfn_lint::engine::Engine;
use cfn_lint::template::Template;

/// A single lint match/issue returned to Python.
#[pyclass]
#[derive(Clone)]
struct Match {
    #[pyo3(get)]
    rule_id: String,
    #[pyo3(get)]
    message: String,
    #[pyo3(get)]
    severity: String,
    #[pyo3(get)]
    line_start: u32,
    #[pyo3(get)]
    column_start: u32,
    #[pyo3(get)]
    line_end: u32,
    #[pyo3(get)]
    column_end: u32,
}

#[pymethods]
impl Match {
    fn __repr__(&self) -> String {
        format!("Match(rule={}, line={}, message={})", self.rule_id, self.line_start, self.message)
    }
}

/// Validate a CloudFormation template string.
/// Returns a list of Match objects.
#[pyfunction]
#[pyo3(signature = (template, regions=None, ignore_checks=None, include_checks=None, include_experimental=None, configure_rules=None, mandatory_checks=None))]
fn validate(
    template: &str,
    regions: Option<Vec<String>>,
    ignore_checks: Option<Vec<String>>,
    include_checks: Option<Vec<String>>,
    include_experimental: Option<bool>,
    configure_rules: Option<&Bound<'_, PyDict>>,
    mandatory_checks: Option<Vec<String>>,
) -> PyResult<Vec<Match>> {
    let regions = regions.unwrap_or_else(|| vec!["us-east-1".to_string()]);
    let ignore = ignore_checks.unwrap_or_default();
    let include = include_checks.unwrap_or_default();
    let mandatory = mandatory_checks.unwrap_or_default();
    let experimental = include_experimental.unwrap_or(false);

    // Build config
    let mut config = cfn_lint::config::Config::default();
    config.regions = regions.clone();
    config.ignore_checks = ignore;
    config.include_checks = include;
    config.mandatory_checks = mandatory;
    config.include_experimental = experimental;

    // Parse configure_rules from Python dict
    if let Some(rules_dict) = configure_rules {
        for (key, value) in rules_dict.iter() {
            let rule_id: String = key.extract()?;
            if let Ok(rule_config) = value.downcast::<PyDict>() {
                let mut cfg = std::collections::HashMap::new();
                for (k, v) in rule_config.iter() {
                    let k: String = k.extract()?;
                    if let Ok(b) = v.extract::<bool>() {
                        cfg.insert(k, serde_json::Value::Bool(b));
                    } else if let Ok(s) = v.extract::<String>() {
                        cfg.insert(k, serde_json::Value::String(s));
                    } else if let Ok(n) = v.extract::<i64>() {
                        cfg.insert(k, serde_json::Value::Number(n.into()));
                    }
                }
                config.configure_rules.insert(rule_id, cfg);
            }
        }
    }

    // Parse
    let ast = parser::parse(template)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Parse error: {}", e)))?;

    // Merge template metadata
    config.merge_template_metadata(&ast);

    // Build template
    let tmpl = Template::from_ast(&ast)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Template error: {}", e)))?;

    // Create engine
    let mut engine = Engine::new();

    // Validate
    let issues = engine.validate(&tmpl, &ast, &config.regions);

    // Filter using config
    let matches: Vec<Match> = issues.into_iter()
        .filter(|i| {
            let rid = i.rule_id.as_deref().unwrap_or("");
            !config.is_ignored(rid)
        })
        .filter(|i| {
            let rid = i.rule_id.as_deref().unwrap_or("");
            let is_experimental = rid.starts_with('I');
            config.is_included(rid, is_experimental)
        })
        .map(|i| {
            let rid = i.rule_id.as_deref().unwrap_or("");
            let severity = match rid.chars().next() {
                Some('W') => "warning".to_string(),
                Some('I') => "informational".to_string(),
                _ => "error".to_string(),
            };
            Match {
                rule_id: i.rule_id.unwrap_or_default(),
                message: i.message,
                severity,
                line_start: i.span.start.line,
                column_start: i.span.start.column,
                line_end: i.span.end.line,
                column_end: i.span.end.column,
            }
        })
        .collect();

    Ok(matches)
}

/// Parse a template and return the structure as a dict.
#[pyfunction]
fn parse_template(template: &str) -> PyResult<String> {
    let ast = parser::parse(template)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Parse error: {}", e)))?;

    // Return a JSON representation of the context
    let ctx = cfn_ast::context::Context::from_ast(Arc::new(ast));
    let info = serde_json::json!({
        "resources": ctx.resources.keys().collect::<Vec<_>>(),
        "parameters": ctx.parameters.keys().collect::<Vec<_>>(),
        "conditions": ctx.conditions.keys().collect::<Vec<_>>(),
        "outputs": ctx.outputs.keys().collect::<Vec<_>>(),
        "mappings": ctx.mappings.keys().collect::<Vec<_>>(),
    });
    Ok(info.to_string())
}

/// Python module definition.
#[pymodule]
fn cfn_lint_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(validate, m)?)?;
    m.add_function(wrap_pyfunction!(parse_template, m)?)?;
    m.add_class::<Match>()?;
    Ok(())
}
