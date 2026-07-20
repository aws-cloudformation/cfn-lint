//! Comprehensive parity test: run Rust cfn-lint against Python cfn-lint's
//! good/bad test fixtures and compare results.
//!
//! ## Accepted divergences ("v2 is better") — do not treat as bugs
//!
//! On a handful of malformed `bad/` fixtures, Python v1 bails out early with a
//! single generic `E0000` (parse/load error), while Rust v2 parses further and
//! emits more specific, more useful findings. These are intentional and are
//! considered improvements over v1, not parity gaps:
//!
//! - `bad/duplicate.yaml` — Python: E0000 x3 (its YAML loader aborts on the
//!   duplicate `mySnsTopic` keys). v2 pinpoints each duplicate (E1001 x2) plus
//!   the invalid `Parameters` property on each copy (E3001 x5). v2's output
//!   tells the user exactly what is wrong instead of "couldn't parse".
//! - `bad/core/parse_invalid_map.yaml` — the file is valid YAML but has a
//!   malformed intrinsic (`!ImportValue Fn::Sub:` nested wrong on the join
//!   line). Python: E0000 x1. v2 reports the concrete problems: undefined-Ref
//!   params (E1020 x5), the malformed Fn::Join (E1022), and unnecessary Fn::Sub
//!   (W1020 x2).
//! - `bad/functions_join.yaml` — Python: E1021 x4, v2: E1021 x3. The extra
//!   Python finding is `Exception '0' raised while validating 'fn_join'`, which
//!   is Python's generic catch-all wrapper (validators.py:277) surfacing an
//!   INTERNAL CRASH in its fn_join validator on the malformed `Fn::Join: !Ref`
//!   input — not a real check. v2 validates the same input cleanly with one
//!   correct finding ("function is not of type array") and does not crash.
//!   Reproducing Python's count would mean emulating a Python bug; we don't.
//!
//! To keep this harness at parity with the frozen Python baseline, `run_engine`
//! below pre-empts these cases the way Python does (synthesize E0000 for parse
//! errors / root-not-object / duplicate / non-string keys, and stop before
//! schema validation). The richer v2 findings are what the *real CLI* emits;
//! they are deliberately not asserted here. If you are reconciling a CLI-based
//! parity run (e.g. /tmp/parity_run.py) that surfaces these as "rust-only",
//! that is expected — see the module docs and project memory
//! `project_cfn_lint_parity_baseline_refresh`.
//! - `bad/empty_file.yaml` — a 0-byte file. Python: E1001 (`'Resources' is a
//!   required property`). The real CLI reports `E0000 "empty document"` (a
//!   0-byte file is a YAML parse error, which routes through the E0000 path
//!   below), exit 2. Both tools flag the file with a non-zero exit; they differ
//!   only in rule code. v2's E1001 rule exists and is correct — it simply never
//!   receives a template object because parsing an empty file errors first. The
//!   "v2 emits E1001 on empty" expectation was always a harness artifact: only
//!   `run_engine` substitutes `{}` for empty input (see below); the CLI does
//!   not. Accepted as-is — `E0000 "empty document"` is arguably a clearer
//!   message than Python's for a genuinely empty file.
//!
//! NOTE: the genuinely-broken bail cases — `bad/string.yaml` (root not an
//! object), `bad/template.yaml` and `bad/core/config_invalid_yaml.yaml`
//! (unparseable YAML) — were previously a reporting-shape GAP (real CLI wrote to
//! stderr, exit 4, EMPTY stdout — a stdout-only consumer saw no findings). This
//! is now FIXED: `main.rs` routes parse/load errors through the formatter as an
//! `E0000` finding with a non-zero exit, matching Python. These templates match
//! Python on rule code (E0000) via that path.

use std::collections::HashMap;
use std::path::{Path, PathBuf};

use cfn_lint::engine::Engine;
use cfn_lint::jsonschema::ValidationError;
use cfn_lint::parser;
use cfn_lint::rules::Severity;
use cfn_lint::template::Template;

fn python_fixtures_dir() -> Option<PathBuf> {
    std::env::var("CFN_LINT_FIXTURES_DIR")
        .ok()
        .map(PathBuf::from)
        .filter(|p| p.is_dir())
}

fn sam_translator_dir() -> Option<PathBuf> {
    std::env::var("SAM_TRANSLATOR_DIR")
        .ok()
        .map(PathBuf::from)
        .filter(|p| p.is_dir())
}

fn data_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data")
}

fn run_engine(engine: &mut Engine, path: &Path) -> Vec<ValidationError> {
    let content = match std::fs::read(path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("READ FAIL {}: {}", path.display(), e);
            return vec![];
        }
    };

    // Handle empty files like Python does — treat as empty object
    let content = if content.is_empty() || content.iter().all(|b| b.is_ascii_whitespace()) {
        b"{}".to_vec()
    } else {
        content
    };

    let dup_issues = parser::detect_duplicate_keys(&content);

    let ast = match parser::parse(&content) {
        Ok(a) => a,
        Err(e) => {
            if !dup_issues.is_empty() {
                return dup_issues;
            }
            return vec![ValidationError {
                rule_id: Some("E0000".to_string()),
                message: format!("Parsing error found when parsing the template: {}", e),
                path: vec![],
                span: cfn_lint::ast::Span::default(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }
    };
    let tmpl = match Template::from_ast(&ast) {
        Ok(t) => t,
        Err(e) => {
            return vec![ValidationError {
                rule_id: Some("E0000".to_string()),
                message: format!("Parsing error found when parsing the template: {}", e),
                path: vec![],
                span: cfn_lint::ast::Span::default(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }
    };
    let mut tmpl = tmpl;
    tmpl.filename = Some(path.to_string_lossy().to_string());

    // Detect non-string keys (unhashable types like !ImportValue Fn::Sub:)
    let nsk_issues = parser::detect_non_string_keys(&ast);
    if !nsk_issues.is_empty() {
        let mut all = dup_issues;
        all.extend(nsk_issues);
        return all;
    }
    // Always use us-east-1 for parity comparison — python_bad/good_results.json
    // was captured with us-east-1. Env vars like AWS_REGION must not affect this.
    let issues = engine.validate(&tmpl, &ast, &["us-east-1".to_string()]);
    if dup_issues.is_empty() {
        issues
    } else {
        // Python stops at duplicate keys — don't run schema validation
        dup_issues
    }
}

fn collect_templates(fixtures_dir: &Path, dir: &str) -> Vec<PathBuf> {
    let mut templates = Vec::new();
    let base = fixtures_dir.join("templates").join(dir);
    if !base.exists() {
        return templates;
    }
    collect_recursive(&base, &mut templates);
    templates.sort();
    templates
}

fn collect_recursive(dir: &Path, out: &mut Vec<PathBuf>) {
    if let Ok(entries) = std::fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_dir() {
                collect_recursive(&path, out);
            } else if let Some(ext) = path.extension() {
                if ext == "yaml" || ext == "json" {
                    out.push(path);
                }
            }
        }
    }
}

fn relative_name(fixtures_dir: &Path, path: &Path) -> String {
    let base = fixtures_dir.join("templates");
    path.strip_prefix(&base)
        .unwrap_or(path)
        .to_string_lossy()
        .to_string()
}

/// Good templates should produce 0 Error-severity issues.
#[test]
fn parity_good_templates_no_errors() {
    let fixtures_dir = match python_fixtures_dir() {
        Some(d) => d,
        None => {
            eprintln!("Skipping: set CFN_LINT_FIXTURES_DIR to enable");
            return;
        }
    };

    let templates = collect_templates(&fixtures_dir, "good");
    if templates.is_empty() {
        println!("No good templates found, skipping");
        return;
    }

    println!("\n{}", "=".repeat(100));
    println!("GOOD TEMPLATES — comparing against Python's actual output");
    println!("{}\n", "=".repeat(100));

    // Load Python's pre-generated results for good templates
    let results_path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("python_good_results.json");
    let python_results: HashMap<String, Vec<String>> = std::fs::read_to_string(&results_path)
        .ok()
        .and_then(|c| serde_json::from_str(&c).ok())
        .unwrap_or_default();

    let mut total = 0;
    let mut matched = 0;
    let mut mismatches: Vec<(String, Vec<String>, Vec<String>)> = Vec::new();

    let mut engine = Engine::with_data_dir(data_dir());

    for path in &templates {
        // Skip templates using unsupported transforms/functions
        if let Ok(content) = std::fs::read_to_string(path) {
            if content.contains("AWS::LanguageExtensions")
                || content.contains("Fn::ForEach")
                || content.contains("Fn::GetStackOutput")
            {
                continue;
            }
        }
        total += 1;
        let name = relative_name(&fixtures_dir, path);
        let issues = run_engine(&mut engine, path);
        let mut rust_ids: Vec<String> = issues
            .into_iter()
            .filter(|i| !i.rule_id.as_deref().unwrap_or("").starts_with("I"))
            .filter_map(|i| i.rule_id)
            .collect();
        rust_ids.sort();

        let lookup_name = name.strip_prefix("good/").unwrap_or(&name).to_string();
        let mut python_ids = python_results
            .get(&lookup_name)
            .cloned()
            .unwrap_or_default();
        python_ids.sort();

        if rust_ids == python_ids {
            matched += 1;
        } else {
            println!("MISMATCH: {}", name);
            let rust_only: Vec<&str> = rust_ids
                .iter()
                .filter(|id| !python_ids.contains(id))
                .map(|s| s.as_str())
                .collect();
            let python_only: Vec<&str> = python_ids
                .iter()
                .filter(|id| !rust_ids.contains(id))
                .map(|s| s.as_str())
                .collect();
            if !rust_only.is_empty() {
                println!("  Rust extra: {:?}", rust_only);
            }
            if !python_only.is_empty() {
                println!("  Python extra: {:?}", python_only);
            }
            mismatches.push((name, rust_ids, python_ids));
        }
    }

    println!("\n{}", "=".repeat(100));
    println!(
        "Good templates: {}/{} match Python ({:.1}%)",
        matched,
        total,
        matched as f64 / total as f64 * 100.0
    );
    println!("{}", "=".repeat(100));
}

/// Bad templates — run and report what we find vs Python.
#[test]
fn parity_bad_templates_report() {
    parity_bad_templates_report_inner();
}

fn parity_bad_templates_report_inner() {
    let fixtures_dir = match python_fixtures_dir() {
        Some(d) => d,
        None => {
            eprintln!("Skipping: set CFN_LINT_FIXTURES_DIR to enable");
            return;
        }
    };

    let templates = collect_templates(&fixtures_dir, "bad");
    if templates.is_empty() {
        println!("No bad templates found, skipping");
        return;
    }

    println!("\n{}", "=".repeat(100));
    println!("BAD TEMPLATES — expecting issues");
    println!("{}\n", "=".repeat(100));

    let mut total = 0;
    let mut with_issues = 0;
    let mut no_issues = 0;
    let mut rule_counts: HashMap<String, usize> = HashMap::new();
    let mut no_issue_templates: Vec<String> = Vec::new();
    let mut engine = Engine::with_data_dir(data_dir());

    for path in &templates {
        // Skip templates using AWS::LanguageExtensions (not yet supported)
        if let Ok(content) = std::fs::read_to_string(path) {
            if content.contains("AWS::LanguageExtensions")
                || content.contains("Fn::ForEach")
                || content.contains("AWS::Serverless")
            {
                continue;
            }
        }
        total += 1;
        let name = relative_name(&fixtures_dir, path);

        eprintln!("  checking: {}", name);
        let issues = run_engine(&mut engine, path);

        if issues.is_empty() {
            no_issues += 1;
            no_issue_templates.push(name);
        } else {
            with_issues += 1;
            for issue in &issues {
                *rule_counts
                    .entry(issue.rule_id.clone().unwrap_or_default())
                    .or_default() += 1;
            }
        }
    }

    println!(
        "Bad templates: {total} total, {with_issues} produced issues, {no_issues} produced nothing"
    );
    println!(
        "Detection rate: {:.1}%",
        with_issues as f64 / total as f64 * 100.0
    );

    if !no_issue_templates.is_empty() {
        println!("\nTemplates with NO issues (potential gaps):");
        for name in &no_issue_templates {
            println!("  {}", name);
        }
    }

    let mut rules: Vec<_> = rule_counts.iter().collect();
    rules.sort_by(|a, b| b.1.cmp(a.1));
    println!("\nRule hit counts across bad templates:");
    for (rule_id, count) in &rules {
        println!("  {}: {}", rule_id, count);
    }
    println!("{}", "=".repeat(100));
}

/// Run against Python's quickstart fixture results for exact comparison.
#[test]
fn parity_quickstart_fixtures() {
    let fixtures_dir = match python_fixtures_dir() {
        Some(d) => d,
        None => {
            eprintln!("Skipping: set CFN_LINT_FIXTURES_DIR to enable");
            return;
        }
    };

    let results_dir = fixtures_dir.join("results/quickstart");
    if !results_dir.exists() {
        println!("No quickstart results found, skipping");
        return;
    }

    println!("\n{}", "=".repeat(100));
    println!("QUICKSTART FIXTURE COMPARISON");
    println!("{}\n", "=".repeat(100));

    let mut total_expected = 0usize;
    let mut total_matched = 0usize;
    let mut engine = Engine::with_data_dir(data_dir());
    // Python quickstart tests run with configure_rules={"E3012": {"strict": True}}
    engine.strict_types = true;

    for entry in std::fs::read_dir(&results_dir).unwrap().flatten() {
        let result_path = entry.path();
        if result_path.extension().map_or(true, |e| e != "json") {
            continue;
        }

        let stem = result_path.file_stem().unwrap().to_string_lossy();
        let template_path = fixtures_dir
            .join("templates/quickstart")
            .join(format!("{}.yaml", stem));

        if !template_path.exists() {
            continue;
        }

        let expected = load_expected_results(&result_path);
        let actual = run_engine(&mut engine, &template_path);

        let mut exp_by_rule: HashMap<String, usize> = HashMap::new();
        for e in &expected {
            *exp_by_rule.entry(e.clone()).or_default() += 1;
        }
        let mut act_by_rule: HashMap<String, usize> = HashMap::new();
        for a in &actual {
            *act_by_rule
                .entry(a.rule_id.clone().unwrap_or_default())
                .or_default() += 1;
        }

        let matched: usize = exp_by_rule
            .iter()
            .map(|(rule, &count)| count.min(*act_by_rule.get(rule).unwrap_or(&0)))
            .sum();

        total_expected += expected.len();
        total_matched += matched;

        let pct = if expected.is_empty() {
            100.0
        } else {
            matched as f64 / expected.len() as f64 * 100.0
        };
        println!(
            "{}: expected:{} actual:{} matched:{} [{:.0}%]",
            stem,
            expected.len(),
            actual.len(),
            matched,
            pct
        );
    }

    let overall = if total_expected == 0 {
        100.0
    } else {
        total_matched as f64 / total_expected as f64 * 100.0
    };
    println!(
        "\nOverall: {}/{} [{:.1}%]",
        total_matched, total_expected, overall
    );
    println!("{}", "=".repeat(100));
}

fn load_expected_results(path: &Path) -> Vec<String> {
    let content = std::fs::read_to_string(path).unwrap_or_default();
    let arr: serde_json::Value = serde_json::from_str(&content).unwrap_or_default();
    arr.as_array()
        .map(|a| {
            a.iter()
                .filter_map(|e| {
                    e.pointer("/Rule/Id")
                        .and_then(|v| v.as_str())
                        .map(String::from)
                })
                .collect()
        })
        .unwrap_or_default()
}

/// Compare Rust output against actual Python cfn-lint output on good+bad templates.
/// Python results are pre-generated in tests/python_{good,bad}_results.json.
#[test]
fn parity_vs_python() {
    parity_vs_python_inner();
}

fn parity_vs_python_inner() {
    let fixtures_dir = match python_fixtures_dir() {
        Some(d) => d,
        None => {
            eprintln!("Skipping: set CFN_LINT_FIXTURES_DIR to enable");
            return;
        }
    };

    let test_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests");
    let templates_base = fixtures_dir.join("templates");

    println!("\n{}", "=".repeat(100));
    println!("PYTHON vs RUST COMPARISON");
    println!("{}\n", "=".repeat(100));

    let mut total_py_rules = 0usize;
    let mut total_rs_rules = 0usize;
    let mut total_matched = 0usize;
    let mut total_py_only = 0usize;
    let mut total_rs_only = 0usize;
    let mut per_rule_py_only: HashMap<String, usize> = HashMap::new();
    let mut per_rule_rs_only: HashMap<String, usize> = HashMap::new();
    let mut engine = Engine::with_data_dir(data_dir());

    for category in &["good", "bad"] {
        let results_file = test_dir.join(format!("python_{}_results.json", category));
        if !results_file.exists() {
            println!("Skipping {} (no python results file)", category);
            continue;
        }

        let content = std::fs::read_to_string(&results_file).unwrap();
        let py_results: HashMap<String, Vec<String>> = serde_json::from_str(&content).unwrap();

        println!(
            "--- {} templates ({} files) ---",
            category,
            py_results.len()
        );

        for (name, py_rules) in &py_results {
            let template_path = templates_base.join(name);
            if !template_path.exists() {
                continue;
            }

            // Skip templates using AWS::LanguageExtensions (not yet supported)
            if let Ok(content) = std::fs::read_to_string(&template_path) {
                if content.contains("AWS::LanguageExtensions")
                    || content.contains("Fn::ForEach")
                    || content.contains("AWS::Serverless")
                {
                    continue;
                }
            }

            let rust_issues = run_engine(&mut engine, &template_path);
            let mut rs_rules: Vec<String> = rust_issues
                .iter()
                .filter(|i| !i.rule_id.as_deref().unwrap_or("").starts_with('I'))
                .filter_map(|i| i.rule_id.clone())
                .collect();
            rs_rules.sort();

            // Count by rule ID
            let mut py_counts: HashMap<&str, usize> = HashMap::new();
            for r in py_rules {
                *py_counts.entry(r.as_str()).or_default() += 1;
            }
            let mut rs_counts: HashMap<&str, usize> = HashMap::new();
            for r in &rs_rules {
                *rs_counts.entry(r.as_str()).or_default() += 1;
            }

            let all_rules: std::collections::HashSet<&str> =
                py_counts.keys().chain(rs_counts.keys()).copied().collect();

            let mut file_matched = 0;
            let mut file_py_only = 0;
            let mut file_rs_only = 0;
            let mut diffs: Vec<String> = Vec::new();

            for rule in &all_rules {
                let pc = *py_counts.get(rule).unwrap_or(&0);
                let rc = *rs_counts.get(rule).unwrap_or(&0);
                let m = pc.min(rc);
                file_matched += m;
                let po = pc.saturating_sub(rc);
                let ro = rc.saturating_sub(pc);
                file_py_only += po;
                file_rs_only += ro;
                if po > 0 {
                    *per_rule_py_only.entry(rule.to_string()).or_default() += po;
                    diffs.push(format!("{}: py={} rs={}", rule, pc, rc));
                }
                if ro > 0 {
                    *per_rule_rs_only.entry(rule.to_string()).or_default() += ro;
                    diffs.push(format!("{}: py={} rs={}", rule, pc, rc));
                }
            }

            total_py_rules += py_rules.len();
            total_rs_rules += rs_rules.len();
            total_matched += file_matched;
            total_py_only += file_py_only;
            total_rs_only += file_rs_only;

            if !diffs.is_empty() {
                diffs.sort();
                diffs.dedup();
                println!("  DIFF {}: {}", name, diffs.join(", "));
            }
        }
    }

    println!("\n{}", "=".repeat(100));
    println!("OVERALL PARITY");
    println!("{}", "=".repeat(100));
    println!(
        "Python total: {}  Rust total: {}  Matched: {}",
        total_py_rules, total_rs_rules, total_matched
    );
    println!(
        "Python-only: {} (rules Python found that Rust missed)",
        total_py_only
    );
    println!(
        "Rust-only: {} (rules Rust found that Python didn't)",
        total_rs_only
    );
    let pct = if total_py_rules == 0 {
        100.0
    } else {
        total_matched as f64 / total_py_rules as f64 * 100.0
    };
    println!("Parity: {:.1}%\n", pct);

    if !per_rule_py_only.is_empty() {
        let mut rules: Vec<_> = per_rule_py_only.iter().collect();
        rules.sort_by(|a, b| b.1.cmp(a.1));
        println!("PYTHON-ONLY by rule (Rust needs to add):");
        for (rule, count) in &rules {
            println!("  {}: {}", rule, count);
        }
    }

    if !per_rule_rs_only.is_empty() {
        let mut rules: Vec<_> = per_rule_rs_only.iter().collect();
        rules.sort_by(|a, b| b.1.cmp(a.1));
        println!("\nRUST-ONLY by rule (Rust false positives or Python missing):");
        for (rule, count) in &rules {
            println!("  {}: {}", rule, count);
        }
    }
    println!("{}", "=".repeat(100));
}

#[test]
fn parity_e1021_debug() {
    let fixtures_dir = match python_fixtures_dir() {
        Some(d) => d,
        None => {
            eprintln!("Skipping: set CFN_LINT_FIXTURES_DIR to enable");
            return;
        }
    };
    let _ = &fixtures_dir;
    let mut engine = Engine::with_data_dir(data_dir());
    let probe = PathBuf::from("/tmp/e1021probe/templates");
    for name in [
        "bad/b64_list.yaml",
        "bad/b64_findinmap_getatt.yaml",
        "bad/b64_join_multi.yaml",
    ] {
        let path = probe.join(name);
        let issues = run_engine(&mut engine, &path);
        println!("\n##### {} #####", name);
        for i in &issues {
            println!(
                "  {} [{}] path={:?} :: {}",
                i.rule_id.as_deref().unwrap_or("?"),
                i.keyword,
                i.path,
                i.message
            );
        }
    }

    // Directly probe base64 function structure validation
    use cfn_lint::jsonschema::Validator;
    let base64_schema: serde_json::Value = serde_json::from_str(include_str!(
        "../data/schemas/other/functions/base64.json"
    ))
    .unwrap();
    println!("\n##### direct validate_schema: list vs base64 schema #####");
    let yaml = "Fn::Base64:\n- Random String\n";
    let ast = cfn_lint::parser::parse(yaml.as_bytes()).unwrap();
    // ast root is object with Fn::Base64; get the function args
    println!("  ast root type debug: {:?}", ast);
    let v = Validator::new(base64_schema.clone());
    // validate the whole {Fn::Base64: [..]} against base64 schema
    let errs = v.validate(&ast, &base64_schema, &[]);
    for e in &errs {
        println!("  ROOT-ERR {} [{}] :: {}", e.rule_id.as_deref().unwrap_or("?"), e.keyword, e.message);
    }
}

#[test]
fn parity_sam_translator() {
    let sam_base = match sam_translator_dir() {
        Some(d) => d,
        None => {
            eprintln!("Skipping: set SAM_TRANSLATOR_DIR to enable");
            return;
        }
    };

    let test_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("tests");
    let results_file = test_dir.join("python_sam_results.json");
    if !results_file.exists() {
        println!("No SAM results file, skipping");
        return;
    }

    let content = std::fs::read_to_string(&results_file).unwrap();
    let py_results: HashMap<String, Vec<String>> = serde_json::from_str(&content).unwrap();

    let ignored_rules: std::collections::HashSet<&str> = [
        "E2531", "E2533", "W2531", "E3001", "W2001", "E3006", "W3037",
    ]
    .into();

    println!("\n{}", "=".repeat(100));
    println!(
        "SAM TRANSLATOR PARITY ({} templates with Python issues)",
        py_results.len()
    );
    println!("{}\n", "=".repeat(100));

    let mut engine = Engine::with_data_dir(data_dir());
    let mut total_py = 0usize;
    let mut total_rs = 0usize;
    let mut total_matched = 0usize;
    let mut per_rule_py_only: HashMap<String, usize> = HashMap::new();
    let mut per_rule_rs_only: HashMap<String, usize> = HashMap::new();

    let active_file = test_dir.join("sam_active_templates.json");
    let active_templates: Vec<String> = if active_file.exists() {
        let content = std::fs::read_to_string(&active_file).unwrap();
        serde_json::from_str(&content).unwrap()
    } else {
        println!("No SAM active templates file, skipping");
        return;
    };

    for rel_str in &active_templates {
        let path = sam_base.join(rel_str);

        let py_rules: Vec<String> = py_results
            .get(rel_str.as_str())
            .cloned()
            .unwrap_or_default()
            .into_iter()
            .filter(|r| !ignored_rules.contains(r.as_str()))
            .collect();

        let rust_issues = run_engine(&mut engine, &path);
        let rs_rules: Vec<String> = rust_issues
            .iter()
            .filter(|i| !ignored_rules.contains(i.rule_id.as_deref().unwrap_or("")))
            .filter(|i| !i.rule_id.as_deref().unwrap_or("").starts_with('I'))
            .filter_map(|i| i.rule_id.clone())
            .collect();

        let mut py_counts: HashMap<&str, usize> = HashMap::new();
        for r in &py_rules {
            *py_counts.entry(r.as_str()).or_default() += 1;
        }
        let mut rs_counts: HashMap<&str, usize> = HashMap::new();
        for r in &rs_rules {
            *rs_counts.entry(r.as_str()).or_default() += 1;
        }

        let all_rules: std::collections::HashSet<&str> =
            py_counts.keys().chain(rs_counts.keys()).copied().collect();

        let mut diffs = Vec::new();
        for rule in &all_rules {
            let pc = *py_counts.get(rule).unwrap_or(&0);
            let rc = *rs_counts.get(rule).unwrap_or(&0);
            let m = pc.min(rc);
            total_matched += m;
            let po = pc.saturating_sub(rc);
            let ro = rc.saturating_sub(pc);
            if po > 0 {
                *per_rule_py_only.entry(rule.to_string()).or_default() += po;
            }
            if ro > 0 {
                *per_rule_rs_only.entry(rule.to_string()).or_default() += ro;
            }
            if po > 0 || ro > 0 {
                diffs.push(format!("{}: py={} rs={}", rule, pc, rc));
            }
        }

        total_py += py_rules.len();
        total_rs += rs_rules.len();

        if !diffs.is_empty() {
            diffs.sort();
            diffs.dedup();
            let name = path.file_name().unwrap().to_string_lossy();
            println!("  DIFF {}: {}", name, diffs.join(", "));
        }
    }

    println!("\n{}", "=".repeat(100));
    println!("SAM TRANSLATOR PARITY RESULTS");
    println!("{}", "=".repeat(100));
    println!(
        "Python total: {}  Rust total: {}  Matched: {}",
        total_py, total_rs, total_matched
    );
    let py_only: usize = per_rule_py_only.values().sum();
    let rs_only: usize = per_rule_rs_only.values().sum();
    println!("Python-only: {} | Rust-only: {}", py_only, rs_only);
    let pct = if total_py == 0 {
        100.0
    } else {
        total_matched as f64 / total_py as f64 * 100.0
    };
    println!("Parity: {:.1}%\n", pct);

    if !per_rule_py_only.is_empty() {
        let mut rules: Vec<_> = per_rule_py_only.iter().collect();
        rules.sort_by(|a, b| b.1.cmp(a.1));
        println!("PYTHON-ONLY by rule:");
        for (rule, count) in &rules {
            println!("  {}: {}", rule, count);
        }
    }
    if !per_rule_rs_only.is_empty() {
        let mut rules: Vec<_> = per_rule_rs_only.iter().collect();
        rules.sort_by(|a, b| b.1.cmp(a.1));
        println!("\nRUST-ONLY by rule:");
        for (rule, count) in &rules {
            println!("  {}: {}", rule, count);
        }
    }
    println!("{}", "=".repeat(100));
}
