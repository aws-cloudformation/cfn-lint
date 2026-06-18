use cfn_lint::config::{Config, ConfigOverrides};
use cfn_lint::engine::Engine;
use cfn_lint::formatters::{get_formatter, ValidationResult};
use cfn_lint::parser;
use cfn_lint::schema::update_schemas;
use cfn_lint::template::Template;

use clap::Parser;
use std::collections::HashMap;
use std::path::PathBuf;
use std::process;

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

    /// When to return non-zero exit code: "informational", "warning", or "error"
    #[arg(long = "non-zero-exit-code", default_value = "error")]
    non_zero_exit_code: String,

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

    // Try relative to the binary
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

fn main() {
    let cli = Cli::parse();
    let list_rules = cli.list_rules;
    let update_schemas_flag = cli.update_schemas;
    let force = cli.force;
    let output_file = cli.output_file;

    // Merge positional templates with -t/--template flag
    let mut templates = cli.template;
    templates.extend(cli.templates_positional);

    // Parse --configure-rule flags
    let configure_rules = parse_configure_rules(&cli.configure_rule);

    let config = match Config::load(ConfigOverrides {
        templates,
        format: if cli.format != "parseable" { Some(cli.format) } else { None },
        regions: cli.regions,
        include_checks: cli.include_checks,
        ignore_checks: cli.ignore_checks,
        include_experimental: if cli.include_experimental { Some(true) } else { None },
        schema_dir: cli.schema_dir,
        config_file: cli.config_file,
        configure_rules,
        append_rules: cli.append_rules,
        registry_schemas: cli.registry_schemas,
        ignore_templates: cli.ignore_templates,
        non_zero_exit_code: if cli.non_zero_exit_code != "error" {
            Some(cli.non_zero_exit_code)
        } else {
            None
        },
        override_spec: cli.override_spec,
    }) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Error loading config: {}", e);
            process::exit(1);
        }
    };

    if update_schemas_flag {
        let data_dir = config
            .schema_dir
            .clone()
            .or_else(|| find_schema_dir(&None))
            .unwrap_or_else(|| PathBuf::from("data"));
        if let Err(e) = update_schemas(&data_dir, &config.regions, force) {
            eprintln!("Error updating schemas: {}", e);
            process::exit(1);
        }
        eprintln!("Schemas updated successfully");
        process::exit(0);
    }

    let mut engine = match find_schema_dir(&config.schema_dir) {
        Some(dir) => Engine::with_data_dir(dir),
        None => Engine::new(),
    };

    if let Some(custom_rules_path) = &cli.custom_rules {
        match cfn_lint::custom_rules::load_custom_rules(custom_rules_path) {
            Ok(rules) => engine.register_custom_rules(rules),
            Err(e) => {
                eprintln!("Error loading custom rules: {}", e);
                process::exit(1);
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
        for (_, line) in lines {
            println!("{}", line);
        }
        process::exit(0);
    }

    if config.templates.is_empty() {
        eprintln!("Error: no template files specified");
        process::exit(1);
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
                eprintln!("Error reading {}: {}", filename, e);
                process::exit(1);
            }
        };

        let ast = match parser::parse(&content) {
            Ok(a) => a,
            Err(_e) => {
                eprintln!("Error parsing {}: {}", filename, _e);
                process::exit(4);
            }
        };

        let tmpl = match Template::from_ast(&ast) {
            Ok(t) => t,
            Err(e) => {
                eprintln!("Error loading {}: {}", filename, e);
                process::exit(4);
            }
        };

        let issues = engine.validate(&tmpl, &ast, &config.regions);

        // Apply include/exclude filters
        // Python cfn-lint excludes I-rules by default; include only if user
        // explicitly passes `-c I` or `-c I3011` etc.
        let i_rules_included = config
            .include_checks
            .iter()
            .any(|c| c.starts_with('I'));
        let filtered: Vec<_> = issues
            .into_iter()
            .filter(|issue| {
                let rid = match &issue.rule_id {
                    Some(r) => r.as_str(),
                    None => return true,
                };
                let dominated_by_include = config.include_checks.is_empty()
                    || config
                        .include_checks
                        .iter()
                        .any(|i| rid.starts_with(i));
                let excluded = config
                    .ignore_checks
                    .iter()
                    .any(|e| rid.starts_with(e));
                // Exclude I-rules unless explicitly included
                if rid.starts_with('I') && !i_rules_included {
                    return false;
                }
                dominated_by_include && !excluded
            })
            .collect();

        all_results.push(ValidationResult {
            filename: (*filename).clone(),
            issues: filtered,
        });
    }

    let formatter = get_formatter(&config.format);
    let output = formatter.format(&all_results);
    if !output.is_empty() {
        if let Some(ref path) = output_file {
            if let Err(e) = std::fs::write(path, &output) {
                eprintln!("Error writing output to {}: {}", path.display(), e);
                process::exit(6);
            }
        } else {
            println!("{}", output);
        }
    }

    // Determine exit code based on --non-zero-exit-code threshold
    let has_errors = all_results
        .iter()
        .any(|r| r.issues.iter().any(|i| i.rule_id.as_ref().map_or(true, |id| id.starts_with('E'))));
    let has_warnings = all_results
        .iter()
        .any(|r| r.issues.iter().any(|i| i.rule_id.as_ref().map_or(false, |id| id.starts_with('W'))));
    let has_informational = all_results
        .iter()
        .any(|r| r.issues.iter().any(|i| i.rule_id.as_ref().map_or(false, |id| id.starts_with('I'))));

    let exit_code = match config.non_zero_exit_code.as_str() {
        "informational" => {
            if has_errors || has_warnings || has_informational { 2 } else { 0 }
        }
        "warning" => {
            if has_errors || has_warnings { 2 } else { 0 }
        }
        _ => {
            // "error" (default)
            if has_errors { 2 } else { 0 }
        }
    };

    process::exit(exit_code);
}
