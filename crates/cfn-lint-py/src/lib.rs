use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::panic::AssertUnwindSafe;
use std::sync::Arc;

use cfn_ast::parser;
use cfn_lint::engine::Engine;
use cfn_lint::template::Template;

/// A single lint match/issue returned to Python.
#[pyclass(skip_from_py_object)]
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
        format!(
            "Match(rule={}, line={}, message={})",
            self.rule_id, self.line_start, self.message
        )
    }
}

/// Extract a human-readable message from a panic payload.
fn panic_payload_to_string(payload: &(dyn std::any::Any + Send)) -> String {
    if let Some(s) = payload.downcast_ref::<&str>() {
        (*s).to_string()
    } else if let Some(s) = payload.downcast_ref::<String>() {
        s.clone()
    } else {
        "unknown panic".to_string()
    }
}

/// Run `f`, catching any panic that unwinds out of the Rust engine and
/// converting it into a `PyRuntimeError`.
///
/// A panic that crossed the FFI boundary uncaught would abort the entire
/// Python interpreter (undefined behavior). Every `#[pyfunction]` body is
/// funneled through this helper so an engine bug degrades to a catchable
/// Python exception instead of a process crash.
fn catch_ffi_panic<F, R>(f: F) -> PyResult<R>
where
    F: FnOnce() -> PyResult<R>,
{
    match std::panic::catch_unwind(AssertUnwindSafe(f)) {
        Ok(result) => result,
        Err(payload) => Err(PyRuntimeError::new_err(format!(
            "cfn-lint engine panicked: {}",
            panic_payload_to_string(payload.as_ref())
        ))),
    }
}

/// Shared core: build config from the Python-facing options, parse and
/// validate `template`, and return the filtered matches. Pure Rust apart from
/// reading the optional `configure_rules` dict.
fn lint_core(
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
    let mut config = cfn_lint::config::Config {
        regions: regions.clone(),
        ignore_checks: ignore,
        include_checks: include,
        mandatory_checks: mandatory,
        include_experimental: experimental,
        ..Default::default()
    };

    // Parse configure_rules from Python dict
    if let Some(rules_dict) = configure_rules {
        for (key, value) in rules_dict.iter() {
            let rule_id: String = key.extract()?;
            if let Ok(rule_config) = value.extract::<pyo3::Bound<'_, PyDict>>() {
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
        .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

    // Merge template metadata
    config.merge_template_metadata(&ast);

    // Build template
    let tmpl = Template::from_ast(&ast)
        .map_err(|e| PyValueError::new_err(format!("Template error: {}", e)))?;

    // Create engine
    let mut engine = Engine::new();

    // Validate
    let issues = engine.validate(&tmpl, &ast, &config.regions);

    // Filter using config
    let matches: Vec<Match> = issues
        .into_iter()
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

/// Lint a CloudFormation template string.
/// Returns a list of `Match` objects.
#[pyfunction]
#[pyo3(signature = (template, regions=None, ignore_checks=None, include_checks=None, include_experimental=None, configure_rules=None, mandatory_checks=None))]
fn lint(
    template: &str,
    regions: Option<Vec<String>>,
    ignore_checks: Option<Vec<String>>,
    include_checks: Option<Vec<String>>,
    include_experimental: Option<bool>,
    configure_rules: Option<&Bound<'_, PyDict>>,
    mandatory_checks: Option<Vec<String>>,
) -> PyResult<Vec<Match>> {
    catch_ffi_panic(move || {
        lint_core(
            template,
            regions,
            ignore_checks,
            include_checks,
            include_experimental,
            configure_rules,
            mandatory_checks,
        )
    })
}

/// Lint a CloudFormation template read from `path`.
/// Returns a list of `Match` objects.
#[pyfunction]
#[pyo3(signature = (path, regions=None, ignore_checks=None, include_checks=None, include_experimental=None, configure_rules=None, mandatory_checks=None))]
fn lint_file(
    path: &str,
    regions: Option<Vec<String>>,
    ignore_checks: Option<Vec<String>>,
    include_checks: Option<Vec<String>>,
    include_experimental: Option<bool>,
    configure_rules: Option<&Bound<'_, PyDict>>,
    mandatory_checks: Option<Vec<String>>,
) -> PyResult<Vec<Match>> {
    catch_ffi_panic(move || {
        let content = std::fs::read_to_string(path)
            .map_err(|e| PyValueError::new_err(format!("Error reading {}: {}", path, e)))?;
        lint_core(
            &content,
            regions,
            ignore_checks,
            include_checks,
            include_experimental,
            configure_rules,
            mandatory_checks,
        )
    })
}

/// Parse a template and return the structure as a JSON string.
#[pyfunction]
fn parse_template(template: &str) -> PyResult<String> {
    catch_ffi_panic(move || {
        let ast = parser::parse(template)
            .map_err(|e| PyValueError::new_err(format!("Parse error: {}", e)))?;

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
    })
}

/// Console entry point backing the `cfn-lint` script.
///
/// Reads `sys.argv`, runs the shared CLI implementation, and returns the
/// process exit code (to be passed to `sys.exit`). Panics inside the engine
/// are converted to `PyRuntimeError` rather than aborting the interpreter.
#[pyfunction]
fn cli_main(py: Python<'_>) -> PyResult<i32> {
    let argv: Vec<String> = py.import("sys")?.getattr("argv")?.extract()?;
    catch_ffi_panic(move || Ok(cfn_lint::cli::run(argv)))
}

/// Python module definition.
///
/// The function name (`_cfn_lint_rs`) determines the generated `PyInit_*`
/// symbol and therefore MUST match the final component of the maturin
/// `module-name` (`cfn_lint._cfn_lint_rs`); otherwise `import cfn_lint` fails
/// at load time with a missing init-function error.
#[pymodule]
fn _cfn_lint_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(lint, m)?)?;
    m.add_function(wrap_pyfunction!(lint_file, m)?)?;
    m.add_function(wrap_pyfunction!(parse_template, m)?)?;
    m.add_function(wrap_pyfunction!(cli_main, m)?)?;
    m.add_class::<Match>()?;
    Ok(())
}
