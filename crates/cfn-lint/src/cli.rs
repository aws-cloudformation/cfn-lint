//! Command-line interface for cfn-lint.
//!
//! The core logic lives in [`run`], which returns an exit code instead of
//! calling [`std::process::exit`]. This lets the CLI be driven both from the
//! `cfn-lint` binary (see `main.rs`) and from the Python bindings' `cli_main`
//! console entry point without terminating the host process (which, across the
//! Python FFI boundary, would abort the interpreter).

use crate::ast::Span;
use crate::config::{Config, ConfigOverrides};
use crate::engine::Engine;
use crate::formatters::{get_formatter, ValidationResult};
use crate::jsonschema::ValidationError;
use crate::parser;
use crate::schema::update_schemas;
use crate::template::Template;

use clap::Parser;
use std::collections::HashMap;
use std::io::{self, ErrorKind, Write};
use std::path::{Path, PathBuf};

/// Severity threshold at or above which cfn-lint returns a non-zero exit code.
///
/// C31: modeled as a clap `ValueEnum` so invalid values (typos) are rejected at
/// parse time instead of silently falling back to "error".
#[derive(clap::ValueEnum, Clone, Copy, Debug, PartialEq, Eq)]
enum NonZeroExitCode {
    Informational,
    Warning,
    Error,
}

impl NonZeroExitCode {
    /// Canonical lowercase name used to populate `Config::non_zero_exit_code`.
    fn as_config_str(self) -> &'static str {
        match self {
            NonZeroExitCode::Informational => "informational",
            NonZeroExitCode::Warning => "warning",
            NonZeroExitCode::Error => "error",
        }
    }
}

#[derive(Parser)]
#[command(name = "cfn-lint", about = "CloudFormation template linter")]
struct Cli {
    /// Template files to validate
    #[arg(short = 't', long = "template")]
    template: Vec<String>,

    /// Output format
    #[arg(short = 'f', long, default_value = "parseable")]
    format: String,

    /// List all rules and exit
    #[arg(short = 'l', long)]
    list_rules: bool,

    /// AWS regions to validate against
    #[arg(short = 'r', long)]
    regions: Vec<String>,

    /// Rules to ignore
    #[arg(short = 'i', long)]
    ignore_checks: Vec<String>,

    /// Rules to include
    #[arg(short = 'c', long)]
    include_checks: Vec<String>,

    /// Path to schema data directory
    #[arg(long)]
    schema_dir: Option<PathBuf>,

    /// Path to configuration file
    #[arg(long)]
    config_file: Option<PathBuf>,

    /// Path to custom rules text file
    #[arg(long)]
    custom_rules: Option<PathBuf>,

    /// Download latest CloudFormation schemas and exit
    #[arg(short = 'u', long)]
    update_schemas: bool,

    /// Force full re-download of all schemas (use with --update-schemas)
    #[arg(long)]
    force: bool,

    /// Paths to additional rule directories
    #[arg(short = 'a', long = "append-rules")]
    append_rules: Vec<PathBuf>,

    /// Rule configuration (format: RuleId:key=value)
    #[arg(long = "configure-rule")]
    configure_rule: Vec<String>,

    /// Include experimental rules
    #[arg(long)]
    include_experimental: bool,

    /// Glob patterns for templates to skip
    #[arg(long = "ignore-templates")]
    ignore_templates: Vec<String>,

    /// Severity threshold for returning a non-zero exit code
    #[arg(long = "non-zero-exit-code", value_enum, default_value_t = NonZeroExitCode::Error)]
    non_zero_exit_code: NonZeroExitCode,

    /// Write output to file instead of stdout
    #[arg(long = "output-file")]
    output_file: Option<PathBuf>,

    /// Path to override specification file
    #[arg(short = 'o', long = "override-spec")]
    override_spec: Option<String>,

    /// Paths to registry schema directories
    #[arg(long = "registry-schemas")]
    registry_schemas: Vec<PathBuf>,

    /// Positional template files (alternative to -t/--template)
    #[arg(trailing_var_arg = true)]
    templates_positional: Vec<String>,
}

/// Parse --configure-rule arguments into a HashMap structure.
/// Format: "RuleId:key=value" e.g. "E3012:strict=true"
fn parse_configure_rules(args: &[String]) -> HashMap<String, HashMap<String, serde_json::Value>> {
    let mut result: HashMap<String, HashMap<String, serde_json::Value>> = HashMap::new();
    for arg in args {
        // Split on first ':' to get rule_id and rest
        if let Some((rule_id, rest)) = arg.split_once(':') {
            // Split rest on '=' to get key and value
            if let Some((key, value_str)) = rest.split_once('=') {
                let value = if value_str == "true" {
                    serde_json::Value::Bool(true)
                } else if value_str == "false" {
                    serde_json::Value::Bool(false)
                } else if let Ok(n) = value_str.parse::<i64>() {
                    serde_json::Value::Number(n.into())
                } else {
                    serde_json::Value::String(value_str.to_string())
                };
                result
                    .entry(rule_id.to_string())
                    .or_default()
                    .insert(key.to_string(), value);
            }
        }
    }
    result
}

fn find_schema_dir(cli_schema_dir: &Option<PathBuf>) -> Option<PathBuf> {
    // CLI flag takes priority
    if let Some(dir) = cli_schema_dir {
        if dir.join("schemas").join("providers").is_dir() {
            return Some(dir.clone());
        }
    }

    // Prefer the default cache directory (populated by --update-schemas), which
    // is always the most current/complete set of schemas. `default_cache_dir()`
    // already ends in `/schemas`, so use its parent as the data dir base — the
    // downstream schema provider joins `schemas/providers` onto it.
    if let Some(schemas_dir) = cfn_schema::default_cache_dir() {
        if let Some(cache_base) = schemas_dir.parent() {
            if cache_base.join("schemas").join("providers").is_dir() {
                return Some(cache_base.to_path_buf());
            }
        }
    }

    // Fall back to schemas bundled relative to the binary.
    if let Ok(exe) = std::env::current_exe() {
        if let Some(exe_dir) = exe.parent() {
            let candidate = exe_dir.join("data");
            if candidate.join("schemas").join("providers").is_dir() {
                return Some(candidate);
            }
        }
    }

    None
}

/// C30: Expand each configured template entry as a glob pattern (matching
/// Python cfn-lint, which treats `templates` list entries as globs). If a
/// pattern matches nothing — or is not a valid glob — the literal entry is kept
/// so a later `fs::read` surfaces a proper "file not found" error instead of
/// silently dropping it. Results are de-duplicated while preserving order.
fn expand_template_globs(patterns: &[String]) -> Vec<String> {
    let mut result: Vec<String> = Vec::new();
    let mut seen = std::collections::HashSet::new();
    let mut push_unique = |p: String, result: &mut Vec<String>| {
        if seen.insert(p.clone()) {
            result.push(p);
        }
    };

    for pattern in patterns {
        match glob::glob(pattern) {
            Ok(paths) => {
                let mut matched: Vec<String> = paths
                    .filter_map(Result::ok)
                    .map(|p| p.to_string_lossy().into_owned())
                    .collect();
                if matched.is_empty() {
                    // No matches — keep the literal path so fs errors surface.
                    push_unique(pattern.clone(), &mut result);
                } else {
                    matched.sort();
                    for m in matched {
                        push_unique(m, &mut result);
                    }
                }
            }
            // Invalid glob syntax — treat the entry as a literal path.
            Err(_) => push_unique(pattern.clone(), &mut result),
        }
    }
    result
}

/// Compute the process exit code given the configured severity threshold and
/// which severities were found. Returns 2 when the threshold is met, else 0.
fn exit_code_for(
    threshold: &str,
    has_errors: bool,
    has_warnings: bool,
    has_informational: bool,
) -> i32 {
    let triggered = match threshold {
        "informational" => has_errors || has_warnings || has_informational,
        "warning" => has_errors || has_warnings,
        // "error" (default) and any unexpected value fall back to error-only.
        _ => has_errors,
    };
    if triggered {
        2
    } else {
        0
    }
}

/// Build a template-level E0000 finding for parse/load failures, mirroring
/// Python v1's behavior of reporting these as a finding rather than aborting.
fn e0000(message: String) -> ValidationError {
    ValidationError {
        rule_id: Some("E0000".to_string()),
        message,
        path: vec![],
        keyword: String::new(),
        span: Span::default(),
        unknown: false,
        resolved_from_ref: false,
        context: vec![],
        schema_id: None,
    }
}

/// Outcome of a CLI stdout write.
///
/// C11: the `println!`/`writeln!` macros `unwrap()` their `io::Result`, so a
/// closed downstream pipe (`cfn-lint template.yaml | head`) makes them *panic*
/// with "failed printing to stdout: Broken pipe". In the native binary that
/// panic aborts the process with a backtrace; across the Python FFI boundary
/// `catch_ffi_panic` turns it into a "cfn-lint engine panicked: ..." error.
/// Standard Unix tools (and Python cfn-lint) instead exit quietly. This enum
/// lets the output paths treat a broken pipe as a clean early exit.
#[derive(Debug)]
enum WriteStatus {
    /// The write succeeded.
    Wrote,
    /// The reader end of the pipe closed early. The caller should stop writing
    /// and exit cleanly with its would-be exit code.
    BrokenPipe,
}

/// Write `line` followed by a newline to the (caller-locked) `out` handle,
/// classifying `ErrorKind::BrokenPipe` as a clean early exit rather than a
/// fatal error. Any other I/O error is returned so the caller can report it.
fn write_line(out: &mut impl Write, line: &str) -> io::Result<WriteStatus> {
    match writeln!(out, "{}", line) {
        Ok(()) => Ok(WriteStatus::Wrote),
        Err(e) if e.kind() == ErrorKind::BrokenPipe => Ok(WriteStatus::BrokenPipe),
        Err(e) => Err(e),
    }
}

/// Run the cfn-lint CLI with the provided argument list (including the program
/// name as the first element, matching `std::env::args()` / `sys.argv`).
///
/// Returns the process exit code. This function never calls
/// [`std::process::exit`] so it is safe to invoke across the Python FFI
/// boundary.
pub fn run<I, T>(args: I) -> i32
where
    I: IntoIterator<Item = T>,
    T: Into<std::ffi::OsString> + Clone,
{
    let cli = match Cli::try_parse_from(args) {
        Ok(c) => c,
        Err(e) => {
            // clap prints help/version to stdout and usage errors to stderr,
            // and provides the conventional exit code for each case.
            let _ = e.print();
            return e.exit_code();
        }
    };

    let list_rules = cli.list_rules;
    let update_schemas_flag = cli.update_schemas;
    let force = cli.force;
    let output_file = cli.output_file;

    // Merge positional templates with -t/--template flag
    let mut templates = cli.template;
    templates.extend(cli.templates_positional);

    // Parse --configure-rule flags
    let configure_rules = parse_configure_rules(&cli.configure_rule);

    let mut config = match Config::load(ConfigOverrides {
        templates,
        format: if cli.format != "parseable" {
            Some(cli.format)
        } else {
            None
        },
        regions: cli.regions,
        include_checks: cli.include_checks,
        ignore_checks: cli.ignore_checks,
        include_experimental: if cli.include_experimental {
            Some(true)
        } else {
            None
        },
        schema_dir: cli.schema_dir,
        config_file: cli.config_file,
        configure_rules,
        append_rules: cli.append_rules,
        registry_schemas: cli.registry_schemas,
        ignore_templates: cli.ignore_templates,
        non_zero_exit_code: if cli.non_zero_exit_code != NonZeroExitCode::Error {
            Some(cli.non_zero_exit_code.as_config_str().to_string())
        } else {
            None
        },
        override_spec: cli.override_spec,
        // C37: feed the CLI custom-rules path into the config so it is merged
        // (CLI wins over .cfnlintrc, but a file-only value is still loaded).
        custom_rules: cli.custom_rules.map(|p| p.to_string_lossy().into_owned()),
    }) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Error loading config: {}", e);
            return 1;
        }
    };

    if update_schemas_flag {
        let data_dir = config
            .schema_dir
            .clone()
            .or_else(|| find_schema_dir(&None))
            .or_else(cfn_schema::default_cache_dir)
            .unwrap_or_else(|| PathBuf::from("data"));
        if let Err(e) = update_schemas(&data_dir, &config.regions, force) {
            eprintln!("Error updating schemas: {}", e);
            return 1;
        }
        eprintln!("Schemas updated successfully");
        return 0;
    }

    let mut engine = match find_schema_dir(&config.schema_dir) {
        Some(dir) => Engine::with_data_dir(dir),
        None => {
            // Try to extract bundled schemas on first run
            #[cfg(feature = "bundled")]
            if let Some(cache_dir) = cfn_schema::extract_bundled_schemas() {
                Engine::with_data_dir(cache_dir)
            } else {
                Engine::new()
            }
            #[cfg(not(feature = "bundled"))]
            Engine::new()
        }
    };

    // C37: load custom rules from the MERGED config so a path configured only
    // in .cfnlintrc is honored (the CLI value already took priority during the
    // config merge above).
    if let Some(custom_rules_path) = &config.custom_rules {
        match crate::custom_rules::load_custom_rules(Path::new(custom_rules_path)) {
            Ok(rules) => engine.register_custom_rules(rules),
            Err(e) => {
                eprintln!("Error loading custom rules: {}", e);
                return 1;
            }
        }
    }

    if list_rules {
        let mut lines: Vec<(String, String)> = Vec::new();
        for r in engine.keyword_rules.all_rules() {
            lines.push((
                r.id().to_string(),
                format!("{} {} {}", r.id(), r.severity(), r.short_description()),
            ));
        }
        lines.sort_by(|a, b| a.0.cmp(&b.0));
        // C11: write through a locked stdout handle so a reader closing the
        // pipe early (`cfn-lint --list-rules | head`) is a clean exit instead
        // of a panic. Would-be exit code here is 0 (matches Python cfn-lint).
        let stdout = io::stdout();
        let mut out = stdout.lock();
        for (_, line) in lines {
            match write_line(&mut out, &line) {
                Ok(WriteStatus::Wrote) => {}
                Ok(WriteStatus::BrokenPipe) => return 0,
                Err(e) => {
                    eprintln!("Error writing to stdout: {}", e);
                    return 1;
                }
            }
        }
        return 0;
    }

    // C30: expand glob patterns in the merged template list (Python cfn-lint
    // treats `templates` entries as globs). Done after the config merge so
    // patterns from both the CLI and .cfnlintrc are expanded.
    config.templates = expand_template_globs(&config.templates);

    if config.templates.is_empty() {
        eprintln!("Error: no template files specified");
        return 1;
    }

    // Filter templates against ignore_templates globs
    let templates_to_lint: Vec<&String> = config
        .templates
        .iter()
        .filter(|t| {
            !config.ignore_templates.iter().any(|pattern| {
                glob::Pattern::new(pattern)
                    .map(|p| p.matches(t))
                    .unwrap_or(false)
            })
        })
        .collect();

    let mut all_results = Vec::new();

    for filename in &templates_to_lint {
        let content = match std::fs::read(filename) {
            Ok(c) => c,
            Err(e) => {
                // C29: an unreadable template must not abort the whole run and
                // skip the remaining files. Surface it as an E0000 finding
                // through the normal output path (matches the parse-error
                // handling below and Python v1) and continue.
                all_results.push(ValidationResult {
                    filename: (*filename).clone(),
                    issues: vec![e0000(format!("Error reading template file: {}", e))],
                });
                continue;
            }
        };

        let ast = match parser::parse(&content) {
            Ok(a) => a,
            Err(e) => {
                // Emit the parse failure as an E0000 finding through the normal
                // output path (matches Python v1) instead of writing to stderr
                // and bailing. A stdout-only consumer would otherwise see an
                // empty result and mistake a broken template for a clean one.
                all_results.push(ValidationResult {
                    filename: (*filename).clone(),
                    issues: vec![e0000(format!(
                        "Parsing error found when parsing the template: {}",
                        e
                    ))],
                });
                continue;
            }
        };

        let mut tmpl = match Template::from_ast(&ast) {
            Ok(t) => t,
            Err(e) => {
                // Root-not-object and other load failures: same treatment as
                // parse errors — surface as an E0000 finding, not a stderr bail.
                all_results.push(ValidationResult {
                    filename: (*filename).clone(),
                    issues: vec![e0000(format!(
                        "Parsing error found when parsing the template: {}",
                        e
                    ))],
                });
                continue;
            }
        };
        // Populate the source filename so rules that resolve paths relative to
        // the template (e.g. E3043 nested-stack TemplateURL) can run. Without
        // this, Template::from_ast leaves filename = None and those rules
        // early-return with no findings.
        tmpl.filename = Some((*filename).clone());

        // C6: apply in-template `Metadata.cfn-lint.config` (ignore_checks,
        // include_checks, regions, include_experimental, configure_rules, ...)
        // per template, matching Python cfn-lint 1.53.1's `TemplateArgs`. The
        // Python binding (cfn-lint-py/src/lib.rs) already does this; the binary
        // was silently ignoring template metadata — a parity regression.
        //
        // Clone the merged config so each template's metadata is isolated: a
        // sibling template in the same run must NOT inherit another template's
        // ignore/include list or regions.
        //
        // The metadata regions must feed the `engine.validate` call (not just
        // the issue filter) so region-scoped findings are produced for the
        // template's own regions.
        let mut tmpl_config = config.clone();
        tmpl_config.merge_template_metadata(&ast);

        let issues = engine.validate(&tmpl, &ast, &tmpl_config.regions);

        // C34: apply include/exclude via Config::is_ignored / is_included (the
        // same path the LSP/Python binding uses) instead of re-implementing the
        // logic inline. This is what enforces the mandatory_checks guard —
        // is_ignored refuses to suppress a mandatory rule, so a mandatory check
        // can no longer be silenced with `-i`. I-rules are treated as
        // experimental (excluded unless explicitly included), matching the
        // previous default behavior. Uses the per-template merged config so
        // metadata ignore_checks/include_checks take effect.
        let filtered: Vec<_> = issues
            .into_iter()
            .filter(|issue| {
                let rid = match &issue.rule_id {
                    Some(r) => r.as_str(),
                    None => return true,
                };
                let is_experimental = rid.starts_with('I');
                !tmpl_config.is_ignored(rid) && tmpl_config.is_included(rid, is_experimental)
            })
            .collect();

        all_results.push(ValidationResult {
            filename: (*filename).clone(),
            issues: filtered,
        });
    }

    let formatter = get_formatter(&config.format);
    let output = formatter.format(&all_results);

    // Determine exit code based on --non-zero-exit-code threshold. Computed
    // before writing so a BrokenPipe mid-write can still return the would-be
    // exit code (matches Python cfn-lint, which reports its real code even when
    // piped to `head`).
    let has_errors = all_results.iter().any(|r| {
        r.issues
            .iter()
            .any(|i| i.rule_id.as_ref().is_none_or(|id| id.starts_with('E')))
    });
    let has_warnings = all_results.iter().any(|r| {
        r.issues
            .iter()
            .any(|i| i.rule_id.as_ref().is_some_and(|id| id.starts_with('W')))
    });
    let has_informational = all_results.iter().any(|r| {
        r.issues
            .iter()
            .any(|i| i.rule_id.as_ref().is_some_and(|id| id.starts_with('I')))
    });

    let exit_code = exit_code_for(
        &config.non_zero_exit_code,
        has_errors,
        has_warnings,
        has_informational,
    );

    if !output.is_empty() {
        if let Some(ref path) = output_file {
            if let Err(e) = std::fs::write(path, &output) {
                eprintln!("Error writing output to {}: {}", path.display(), e);
                return 6;
            }
        } else {
            // C11: write through a locked stdout handle; treat a closed pipe as
            // a clean early exit (return the would-be exit code) rather than a
            // panic on Broken pipe.
            let stdout = io::stdout();
            let mut out = stdout.lock();
            match write_line(&mut out, &output) {
                Ok(WriteStatus::Wrote) => {}
                Ok(WriteStatus::BrokenPipe) => return exit_code,
                Err(e) => {
                    eprintln!("Error writing to stdout: {}", e);
                    return 1;
                }
            }
        }
    }

    exit_code
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn no_templates_returns_1() {
        assert_eq!(run(["cfn-lint"]), 1);
    }

    #[test]
    fn list_rules_returns_0() {
        assert_eq!(run(["cfn-lint", "--list-rules"]), 0);
    }

    #[test]
    fn unknown_flag_returns_clap_usage_code() {
        // clap uses exit code 2 for argument/usage errors.
        assert_eq!(run(["cfn-lint", "--definitely-not-a-flag"]), 2);
    }

    #[test]
    fn help_returns_0() {
        assert_eq!(run(["cfn-lint", "--help"]), 0);
    }

    #[test]
    fn missing_template_file_reports_e0000_and_exits_2() {
        // C29: an unreadable/nonexistent template is surfaced as an E0000
        // error finding through the normal output path (not a stderr bail),
        // so the run continues and exits 2 (error severity) rather than 1.
        assert_eq!(
            run(["cfn-lint", "-t", "/nonexistent/path/to/template.yaml"]),
            2
        );
    }

    #[test]
    fn malformed_template_reports_e0000_and_exits_2() {
        // A template whose root is not a mapping is a load error surfaced as
        // an E0000 finding, which is an error-severity result -> exit code 2.
        let mut file = tempfile::Builder::new().suffix(".yaml").tempfile().unwrap();
        use std::io::Write;
        write!(file, "- just\n- a\n- list\n").unwrap();
        let path = file.path().to_str().unwrap();
        assert_eq!(run(["cfn-lint", "-t", path]), 2);
    }

    // ── C30: glob expansion ────────────────────────────────────────────

    #[test]
    fn glob_expands_wildcard_to_matching_files() {
        use std::io::Write;
        let dir = tempfile::tempdir().unwrap();
        for name in ["a.yaml", "b.yaml", "c.json"] {
            let mut f = std::fs::File::create(dir.path().join(name)).unwrap();
            writeln!(f, "Resources: {{}}").unwrap();
        }
        let pattern = dir.path().join("*.yaml").to_string_lossy().into_owned();

        let expanded = expand_template_globs(&[pattern]);

        assert_eq!(
            expanded.len(),
            2,
            "expected 2 .yaml matches: {:?}",
            expanded
        );
        assert!(expanded.iter().all(|p| p.ends_with(".yaml")));
        // Results are sorted for determinism.
        assert!(expanded[0].ends_with("a.yaml"));
        assert!(expanded[1].ends_with("b.yaml"));
    }

    #[test]
    fn glob_no_match_falls_back_to_literal_path() {
        // A non-existent explicit path (no wildcard) must be preserved so that
        // fs::read later surfaces a proper "not found" error, not silence.
        let literal = "/tmp/definitely-does-not-exist-xyz.yaml".to_string();
        let expanded = expand_template_globs(std::slice::from_ref(&literal));
        assert_eq!(expanded, vec![literal]);
    }

    #[test]
    fn glob_wildcard_no_match_falls_back_to_literal() {
        let dir = tempfile::tempdir().unwrap();
        let pattern = dir.path().join("*.nomatch").to_string_lossy().into_owned();
        let expanded = expand_template_globs(std::slice::from_ref(&pattern));
        // Pattern matched nothing → keep the literal so the error surfaces.
        assert_eq!(expanded, vec![pattern]);
    }

    #[test]
    fn glob_deduplicates_overlapping_patterns() {
        use std::io::Write;
        let dir = tempfile::tempdir().unwrap();
        let mut f = std::fs::File::create(dir.path().join("only.yaml")).unwrap();
        writeln!(f, "Resources: {{}}").unwrap();
        let p1 = dir.path().join("*.yaml").to_string_lossy().into_owned();
        let p2 = dir.path().join("only.yaml").to_string_lossy().into_owned();

        let expanded = expand_template_globs(&[p1, p2]);
        assert_eq!(
            expanded.len(),
            1,
            "duplicate paths should collapse: {:?}",
            expanded
        );
    }

    // ── C31: exit-code threshold ───────────────────────────────────────

    #[test]
    fn exit_code_error_threshold() {
        assert_eq!(exit_code_for("error", true, false, false), 2);
        assert_eq!(exit_code_for("error", false, true, false), 0);
        assert_eq!(exit_code_for("error", false, false, true), 0);
        assert_eq!(exit_code_for("error", false, false, false), 0);
    }

    #[test]
    fn exit_code_warning_threshold() {
        assert_eq!(exit_code_for("warning", false, true, false), 2);
        assert_eq!(exit_code_for("warning", true, false, false), 2);
        assert_eq!(exit_code_for("warning", false, false, true), 0);
    }

    #[test]
    fn exit_code_informational_threshold() {
        assert_eq!(exit_code_for("informational", false, false, true), 2);
        assert_eq!(exit_code_for("informational", false, true, false), 2);
        assert_eq!(exit_code_for("informational", false, false, false), 0);
    }

    #[test]
    fn exit_code_unknown_threshold_defaults_to_error_only() {
        // Defense in depth: even if a bad value slips past clap validation
        // (e.g. via a config file), it behaves like "error", never panics.
        assert_eq!(exit_code_for("typo", true, false, false), 2);
        assert_eq!(exit_code_for("typo", false, true, true), 0);
    }

    #[test]
    fn non_zero_exit_code_as_config_str() {
        assert_eq!(
            NonZeroExitCode::Informational.as_config_str(),
            "informational"
        );
        assert_eq!(NonZeroExitCode::Warning.as_config_str(), "warning");
        assert_eq!(NonZeroExitCode::Error.as_config_str(), "error");
    }

    // ── C6: in-template Metadata.cfn-lint.config applied in the CLI loop ────

    /// Bundled schema data dir shipped with this crate, so `run` can perform
    /// real schema validation from within unit tests (same dir the parity
    /// harness uses via `Engine::with_data_dir`).
    fn schema_data_dir() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data")
    }

    /// A minimal template that triggers exactly one error-severity finding —
    /// E3002 (unexpected property `NotARealProperty` on an S3 bucket). Matches
    /// Python cfn-lint 1.53.1, which reports E3002 for the same input. When
    /// `ignore_metadata` is set, the template carries
    /// `Metadata.cfn-lint.config.ignore_checks: [E3002]` to suppress it.
    fn e3002_template(ignore_metadata: bool) -> String {
        let metadata = if ignore_metadata {
            "Metadata:\n  cfn-lint:\n    config:\n      ignore_checks:\n        - E3002\n"
        } else {
            ""
        };
        format!(
            "{metadata}Resources:\n  Bucket:\n    Type: AWS::S3::Bucket\n    Properties:\n      NotARealProperty: true\n"
        )
    }

    /// C6: `Metadata.cfn-lint.config.ignore_checks` must take effect through the
    /// binary's per-template loop (previously silently ignored — a Python-parity
    /// regression), and it must be isolated per template: one template's
    /// metadata must not suppress findings in a sibling template of the same
    /// run.
    #[test]
    fn template_metadata_ignore_checks_applied_via_cli_and_isolated_per_template() {
        use std::io::Write;

        let data_dir = schema_data_dir();
        // Safety net: skip cleanly on a host without provider schemas rather
        // than fail spuriously. The repo ships these under `data/`, so this
        // should not trigger in normal builds/CI.
        if !data_dir.join("schemas").join("providers").is_dir() {
            eprintln!(
                "skipping: provider schemas not present at {}",
                data_dir.display()
            );
            return;
        }
        let data_dir = data_dir.to_str().unwrap().to_string();

        let dir = tempfile::tempdir().unwrap();
        // Template A: E3002 violation, suppressed via in-template metadata.
        let a_path = dir.path().join("a_ignored.yaml");
        std::fs::File::create(&a_path)
            .unwrap()
            .write_all(e3002_template(true).as_bytes())
            .unwrap();
        // Template B: same E3002 violation, NO metadata — must still report.
        let b_path = dir.path().join("b_plain.yaml");
        std::fs::File::create(&b_path)
            .unwrap()
            .write_all(e3002_template(false).as_bytes())
            .unwrap();
        let a = a_path.to_str().unwrap();
        let b = b_path.to_str().unwrap();

        // (1) Template A alone: its metadata suppresses its only error → exit 0.
        assert_eq!(
            run(["cfn-lint", "--schema-dir", &data_dir, "-t", a]),
            0,
            "in-template ignore_checks should suppress E3002 via the CLI path"
        );

        // (2) Template B alone: no metadata → E3002 reported → exit 2.
        assert_eq!(
            run(["cfn-lint", "--schema-dir", &data_dir, "-t", b]),
            2,
            "template without metadata should still report E3002"
        );

        // (3) Both templates in one run, output captured: proves per-template
        // isolation — A's metadata suppresses only A's finding; B (no metadata)
        // still reports E3002, and A's ignore list does not leak into B.
        let out_path = dir.path().join("out.txt");
        assert_eq!(
            run([
                "cfn-lint",
                "--schema-dir",
                &data_dir,
                "--output-file",
                out_path.to_str().unwrap(),
                "-t",
                a,
                "-t",
                b,
            ]),
            2,
            "combined run still errors because sibling B reports E3002"
        );

        let out = std::fs::read_to_string(&out_path).unwrap();
        // Sibling B's E3002 is present (not suppressed by A's metadata)...
        assert!(
            out.lines()
                .any(|l| l.contains("b_plain.yaml") && l.contains("E3002")),
            "expected E3002 for sibling template B, got:\n{out}"
        );
        // ...and A's E3002 is absent (suppressed by its own metadata, no leak).
        assert!(
            !out.lines()
                .any(|l| l.contains("a_ignored.yaml") && l.contains("E3002")),
            "template A's E3002 should be suppressed by its own metadata, got:\n{out}"
        );
    }

    // ── C11: BrokenPipe handling in the stdout output path ─────────────

    /// A writer whose every `write` fails with a configurable `ErrorKind`,
    /// used to drive `write_line`'s error classification without a real pipe.
    struct FailingWriter(ErrorKind);
    impl Write for FailingWriter {
        fn write(&mut self, _buf: &[u8]) -> io::Result<usize> {
            Err(io::Error::new(self.0, "injected error"))
        }
        fn flush(&mut self) -> io::Result<()> {
            Ok(())
        }
    }

    #[test]
    fn write_line_writes_content_with_newline() {
        let mut buf: Vec<u8> = Vec::new();
        let status = write_line(&mut buf, "hello").expect("write should succeed");
        assert!(matches!(status, WriteStatus::Wrote));
        assert_eq!(buf, b"hello\n");
    }

    #[test]
    fn write_line_classifies_broken_pipe_as_clean_exit() {
        let mut w = FailingWriter(ErrorKind::BrokenPipe);
        let status = write_line(&mut w, "anything").expect("BrokenPipe is not a hard error");
        assert!(matches!(status, WriteStatus::BrokenPipe));
    }

    #[test]
    fn write_line_propagates_other_io_errors() {
        let mut w = FailingWriter(ErrorKind::PermissionDenied);
        let err = write_line(&mut w, "anything").expect_err("non-pipe errors must propagate");
        assert_eq!(err.kind(), ErrorKind::PermissionDenied);
    }
}
