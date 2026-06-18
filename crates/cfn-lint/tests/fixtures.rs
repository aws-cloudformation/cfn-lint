use std::path::PathBuf;

use cfn_lint::engine::Engine;
use cfn_lint::formatters::{get_formatter, Formatter, ValidationResult};
use cfn_lint::jsonschema::ValidationError;
use cfn_lint::parser;
use cfn_lint::template::Template;

fn data_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data")
}

fn fixtures_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
}

fn run_template(engine: &mut Engine, path: &std::path::Path) -> Vec<ValidationError> {
    let content = std::fs::read(path).expect("failed to read template");

    let ast = match parser::parse(&content) {
        Ok(a) => a,
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

    engine.validate(&tmpl, &ast, &["us-east-1".to_string()])
}

#[test]
fn fixture_templates() {
    let fixtures = fixtures_dir();
    let templates_dir = fixtures.join("templates");
    let results_dir = fixtures.join("results");

    let mut engine = Engine::with_data_dir(data_dir());

    let mut templates: Vec<PathBuf> = std::fs::read_dir(&templates_dir)
        .expect("failed to read fixtures/templates")
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            p.extension()
                .map_or(false, |ext| ext == "yaml" || ext == "json")
        })
        .collect();
    templates.sort();

    assert!(!templates.is_empty(), "no fixture templates found");

    let mut failures: Vec<String> = Vec::new();

    for template_path in &templates {
        let stem = template_path.file_stem().unwrap().to_string_lossy();
        let results_path = results_dir.join(format!("{}.json", stem));

        let issues = run_template(&mut engine, template_path);

        let results = vec![ValidationResult {
            filename: template_path
                .file_name()
                .unwrap()
                .to_string_lossy()
                .to_string(),
            issues,
        }];

        let actual_json = get_formatter("json").format(&results);
        let actual: serde_json::Value =
            serde_json::from_str(&actual_json).expect("formatter produced invalid JSON");

        if !results_path.exists() {
            // No expected file — write the actual output so the developer can review
            std::fs::write(&results_path, &actual_json).unwrap();
            failures.push(format!(
                "{}: no results file existed, wrote actual output to {}. Review and commit.",
                stem,
                results_path.display()
            ));
            continue;
        }

        let expected_str = std::fs::read_to_string(&results_path).unwrap();
        let expected: serde_json::Value = serde_json::from_str(&expected_str)
            .unwrap_or_else(|e| panic!("{}: invalid results JSON: {}", stem, e));

        if actual != expected {
            failures.push(format!(
                "{}: output mismatch.\n  expected: {}\n  actual:   {}",
                stem,
                serde_json::to_string(&expected).unwrap(),
                serde_json::to_string(&actual).unwrap(),
            ));
        }
    }

    if !failures.is_empty() {
        panic!(
            "\n{} fixture test failure(s):\n\n{}\n",
            failures.len(),
            failures.join("\n\n")
        );
    }
}
