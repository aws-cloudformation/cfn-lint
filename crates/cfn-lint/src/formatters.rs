use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use serde::Serialize;

pub struct ValidationResult {
    pub filename: String,
    pub issues: Vec<ValidationError>,
}

/// Derive severity from the rule_id prefix: E=Error, W=Warning, I=Informational.
fn severity_from_rule_id(rule_id: Option<&str>) -> Severity {
    match rule_id.and_then(|r| r.chars().next()) {
        Some('W') => Severity::Warning,
        Some('I') => Severity::Informational,
        _ => Severity::Error,
    }
}

pub trait Formatter {
    fn format(&self, results: &[ValidationResult]) -> String;
}

pub fn get_formatter(name: &str) -> Box<dyn Formatter> {
    match name {
        "json" => Box::new(JsonFormatter),
        "pretty" => Box::new(PrettyFormatter),
        "junit" => Box::new(JUnitFormatter),
        "sarif" => Box::new(SarifFormatter),
        _ => Box::new(ParseableFormatter),
    }
}

// --- Parseable ---

pub struct ParseableFormatter;

impl Formatter for ParseableFormatter {
    fn format(&self, results: &[ValidationResult]) -> String {
        results
            .iter()
            .flat_map(|r| {
                r.issues.iter().map(move |i| {
                    let rule_id = i.rule_id.as_deref().unwrap_or("");
                    format!(
                        "{}:{}:{}:{}:{}:{}:{}",
                        r.filename,
                        i.span.start.line as usize,
                        i.span.start.column as usize,
                        i.span.end.line as usize,
                        i.span.end.column as usize,
                        rule_id,
                        i.message
                    )
                })
            })
            .collect::<Vec<_>>()
            .join("\n")
    }
}

// --- JSON ---

pub struct JsonFormatter;

#[derive(Serialize)]
struct JsonIssue<'a> {
    filename: &'a str,
    rule_id: &'a str,
    message: &'a str,
    line: usize,
    column: usize,
    severity: &'a str,
}

impl Formatter for JsonFormatter {
    fn format(&self, results: &[ValidationResult]) -> String {
        let items: Vec<JsonIssue> = results
            .iter()
            .flat_map(|r| {
                r.issues.iter().map(move |i| {
                    let rule_id = i.rule_id.as_deref().unwrap_or("");
                    let severity = severity_from_rule_id(i.rule_id.as_deref());
                    JsonIssue {
                        filename: &r.filename,
                        rule_id,
                        message: &i.message,
                        line: i.span.start.line as usize,
                        column: i.span.start.column as usize,
                        severity: severity_str(severity),
                    }
                })
            })
            .collect();
        serde_json::to_string_pretty(&items).unwrap_or_else(|_| "[]".to_string())
    }
}

fn severity_str(s: Severity) -> &'static str {
    match s {
        Severity::Error => "Error",
        Severity::Warning => "Warning",
        Severity::Informational => "Informational",
    }
}

// --- Pretty ---

pub struct PrettyFormatter;

impl Formatter for PrettyFormatter {
    fn format(&self, results: &[ValidationResult]) -> String {
        results
            .iter()
            .flat_map(|r| {
                r.issues.iter().map(move |i| {
                    let rule_id = i.rule_id.as_deref().unwrap_or("");
                    let severity = severity_from_rule_id(i.rule_id.as_deref());
                    let (color, reset) = severity_color(severity);
                    format!(
                        "{}:{}:{}\n  {}[{}] {}: {}{}",
                        r.filename,
                        i.span.start.line as usize,
                        i.span.start.column as usize,
                        color,
                        severity,
                        rule_id,
                        i.message,
                        reset
                    )
                })
            })
            .collect::<Vec<_>>()
            .join("\n")
    }
}

fn severity_color(s: Severity) -> (&'static str, &'static str) {
    match s {
        Severity::Error => ("\x1b[31m", "\x1b[0m"),
        Severity::Warning => ("\x1b[33m", "\x1b[0m"),
        Severity::Informational => ("\x1b[36m", "\x1b[0m"),
    }
}

// --- JUnit XML ---

pub struct JUnitFormatter;

fn xml_escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for ch in s.chars() {
        match ch {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&apos;"),
            // Tab, newline, and carriage return are the only control
            // characters permitted by XML 1.0; keep them verbatim.
            '\t' | '\n' | '\r' => out.push(ch),
            // Strip the remaining XML-1.0-forbidden control characters
            // (0x00–0x08, 0x0B, 0x0C, 0x0E–0x1F). These cannot appear in a
            // well-formed XML document even as numeric character references,
            // so escaping is impossible — they must be dropped. Such bytes
            // can leak from template content into rule messages and would
            // otherwise produce output that JUnit parsers reject.
            c if (c as u32) < 0x20 => {}
            _ => out.push(ch),
        }
    }
    out
}

impl Formatter for JUnitFormatter {
    fn format(&self, results: &[ValidationResult]) -> String {
        let tests = results.len();
        let failures = results
            .iter()
            .filter(|r| {
                r.issues
                    .iter()
                    .any(|i| matches!(severity_from_rule_id(i.rule_id.as_deref()), Severity::Error))
            })
            .count();

        let mut out = String::new();
        out.push_str("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        out.push_str("<testsuites>\n");
        out.push_str(&format!(
            "  <testsuite name=\"cfn-lint\" tests=\"{}\" failures=\"{}\">\n",
            tests, failures
        ));

        for r in results {
            if r.issues.is_empty() {
                out.push_str(&format!(
                    "    <testcase name=\"{}\"/>\n",
                    xml_escape(&r.filename)
                ));
            } else {
                out.push_str(&format!(
                    "    <testcase name=\"{}\">\n",
                    xml_escape(&r.filename)
                ));
                for i in &r.issues {
                    let rule_id = i.rule_id.as_deref().unwrap_or("");
                    let line = i.span.start.line as usize;
                    let col = i.span.start.column as usize;
                    let message_attr =
                        xml_escape(&format!("{} at {}:{}:{}", rule_id, r.filename, line, col));
                    let message_text = xml_escape(&format!("{}: {}", rule_id, i.message));
                    out.push_str(&format!(
                        "      <failure message=\"{}\" type=\"{}\">{}</failure>\n",
                        message_attr,
                        xml_escape(rule_id),
                        message_text
                    ));
                }
                out.push_str("    </testcase>\n");
            }
        }

        out.push_str("  </testsuite>\n");
        out.push_str("</testsuites>\n");
        out
    }
}

// --- SARIF 2.1.0 ---

pub struct SarifFormatter;

/// Map a rule_id prefix to a SARIF level string.
fn sarif_level(rule_id: Option<&str>) -> &'static str {
    match rule_id.and_then(|r| r.chars().next()) {
        Some('W') => "warning",
        Some('I') => "note",
        _ => "error",
    }
}

impl Formatter for SarifFormatter {
    fn format(&self, results: &[ValidationResult]) -> String {
        use std::collections::BTreeMap;

        struct Finding<'a> {
            rule_id: &'a str,
            level: &'static str,
            message: &'a str,
            uri: &'a str,
            start_line: usize,
            start_column: usize,
            end_line: usize,
            end_column: usize,
        }

        let mut findings: Vec<Finding> = Vec::new();
        // BTreeMap keeps rule ids sorted for deterministic output.
        let mut seen_rules: BTreeMap<&str, ()> = BTreeMap::new();

        for r in results {
            for i in &r.issues {
                let rule_id = i.rule_id.as_deref().unwrap_or("unknown");
                let level = sarif_level(i.rule_id.as_deref());
                seen_rules.insert(rule_id, ());
                findings.push(Finding {
                    rule_id,
                    level,
                    message: &i.message,
                    uri: &r.filename,
                    start_line: i.span.start.line as usize,
                    start_column: i.span.start.column as usize,
                    end_line: i.span.end.line as usize,
                    end_column: i.span.end.column as usize,
                });
            }
        }

        let rules: Vec<serde_json::Value> = seen_rules
            .keys()
            .map(|id| {
                serde_json::json!({
                    "id": id,
                    "shortDescription": { "text": id },
                    "helpUri": "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/rules.md"
                })
            })
            .collect();

        let sarif_results: Vec<serde_json::Value> = findings
            .iter()
            .map(|f| {
                serde_json::json!({
                    "ruleId": f.rule_id,
                    "level": f.level,
                    "message": { "text": f.message },
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": f.uri,
                                    "uriBaseId": "EXECUTIONROOT"
                                },
                                "region": {
                                    "startLine": f.start_line,
                                    "startColumn": f.start_column,
                                    "endLine": f.end_line,
                                    "endColumn": f.end_column
                                }
                            }
                        }
                    ]
                })
            })
            .collect();

        let sarif = serde_json::json!({
            "$schema": "https://docs.oasis-open.org/sarif/sarif/v2.1.0/cos02/schemas/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "cfn-lint",
                            "informationUri": "https://github.com/aws-cloudformation/cfn-lint",
                            "version": "2.0.0",
                            "rules": rules
                        }
                    },
                    "results": sarif_results
                }
            ]
        });

        serde_json::to_string_pretty(&sarif).unwrap_or_else(|_| "{}".to_string())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{Position, Span};

    fn sample_results() -> Vec<ValidationResult> {
        vec![ValidationResult {
            filename: "template.yaml".to_string(),
            issues: vec![
                ValidationError {
                    rule_id: Some("E1003".to_string()),
                    message: "Description too long".to_string(),
                    path: vec!["Description".to_string()],
                    span: Span {
                        start: Position { line: 2, column: 1 },
                        end: Position { line: 2, column: 1 },
                    },
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                },
                ValidationError {
                    rule_id: Some("W2001".to_string()),
                    message: "Unused parameter".to_string(),
                    path: vec!["Parameters".to_string(), "Env".to_string()],
                    span: Span {
                        start: Position { line: 5, column: 3 },
                        end: Position { line: 5, column: 3 },
                    },
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                },
            ],
        }]
    }

    #[test]
    fn test_parseable_formatter() {
        let out = ParseableFormatter.format(&sample_results());
        let lines: Vec<&str> = out.lines().collect();
        assert_eq!(lines.len(), 2);
        assert_eq!(lines[0], "template.yaml:2:1:2:1:E1003:Description too long");
        assert_eq!(lines[1], "template.yaml:5:3:5:3:W2001:Unused parameter");
    }

    #[test]
    fn test_json_formatter() {
        let out = JsonFormatter.format(&sample_results());
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        let arr = parsed.as_array().unwrap();
        assert_eq!(arr.len(), 2);
        assert_eq!(arr[0]["filename"], "template.yaml");
        assert_eq!(arr[0]["rule_id"], "E1003");
        assert_eq!(arr[0]["message"], "Description too long");
        assert_eq!(arr[0]["line"], 2);
        assert_eq!(arr[0]["column"], 1);
        assert_eq!(arr[0]["severity"], "Error");
        assert_eq!(arr[1]["rule_id"], "W2001");
        assert_eq!(arr[1]["severity"], "Warning");
    }

    #[test]
    fn test_pretty_formatter() {
        let out = PrettyFormatter.format(&sample_results());
        assert!(out.contains("template.yaml:2:1"));
        assert!(out.contains("\x1b[31m[E] E1003: Description too long\x1b[0m"));
        assert!(out.contains("template.yaml:5:3"));
        assert!(out.contains("\x1b[33m[W] W2001: Unused parameter\x1b[0m"));
    }

    #[test]
    fn test_get_formatter_default() {
        let f = get_formatter("parseable");
        let out = f.format(&sample_results());
        assert!(out.contains("template.yaml:2:1:2:1:E1003"));
    }

    #[test]
    fn test_get_formatter_json() {
        let f = get_formatter("json");
        let out = f.format(&sample_results());
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert!(parsed.is_array());
    }

    #[test]
    fn test_get_formatter_pretty() {
        let f = get_formatter("pretty");
        let out = f.format(&sample_results());
        assert!(out.contains("\x1b[31m"));
    }

    #[test]
    fn test_get_formatter_unknown_defaults_to_parseable() {
        let f = get_formatter("unknown");
        let out = f.format(&sample_results());
        assert!(out.contains("template.yaml:2:1:2:1:E1003"));
    }

    #[test]
    fn test_empty_results() {
        let results: Vec<ValidationResult> = vec![];
        assert_eq!(ParseableFormatter.format(&results), "");
        assert_eq!(JsonFormatter.format(&results), "[]");
        assert_eq!(PrettyFormatter.format(&results), "");
    }

    #[test]
    fn test_informational_severity() {
        let results = vec![ValidationResult {
            filename: "t.yaml".to_string(),
            issues: vec![ValidationError {
                rule_id: Some("I1001".to_string()),
                message: "Info".to_string(),
                path: vec![],
                span: Span {
                    start: Position { line: 1, column: 1 },
                    end: Position { line: 1, column: 1 },
                },
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }],
        }];
        let out = ParseableFormatter.format(&results);
        assert_eq!(out, "t.yaml:1:1:1:1:I1001:Info");

        let out = PrettyFormatter.format(&results);
        assert!(out.contains("\x1b[36m[I] I1001: Info\x1b[0m"));

        let out = JsonFormatter.format(&results);
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(parsed[0]["severity"], "Informational");
    }

    #[test]
    fn test_junit_formatter_basic() {
        let out = JUnitFormatter.format(&sample_results());
        // XML declaration and root elements
        assert!(out.starts_with("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"));
        assert!(out.contains("<testsuites>"));
        assert!(out.contains("</testsuites>"));
        // One template file → tests=1; one file has E1003 (error) → failures=1
        assert!(out.contains("<testsuite name=\"cfn-lint\" tests=\"1\" failures=\"1\">"));
        // Testcase for template.yaml
        assert!(out.contains("<testcase name=\"template.yaml\">"));
        assert!(out.contains("</testcase>"));
        // E1003 failure element
        assert!(out.contains("message=\"E1003 at template.yaml:2:1\""));
        assert!(out.contains("type=\"E1003\""));
        assert!(out.contains(">E1003: Description too long</failure>"));
        // W2001 failure element
        assert!(out.contains("message=\"W2001 at template.yaml:5:3\""));
        assert!(out.contains("type=\"W2001\""));
        assert!(out.contains(">W2001: Unused parameter</failure>"));
    }

    #[test]
    fn test_junit_formatter_empty() {
        let results: Vec<ValidationResult> = vec![];
        let out = JUnitFormatter.format(&results);
        assert!(out.contains("<testsuite name=\"cfn-lint\" tests=\"0\" failures=\"0\">"));
        assert!(out.contains("</testsuite>"));
    }

    #[test]
    fn test_junit_formatter_no_issues_self_closing() {
        let results = vec![ValidationResult {
            filename: "clean.yaml".to_string(),
            issues: vec![],
        }];
        let out = JUnitFormatter.format(&results);
        assert!(out.contains("<testsuite name=\"cfn-lint\" tests=\"1\" failures=\"0\">"));
        assert!(out.contains("<testcase name=\"clean.yaml\"/>"));
        assert!(!out.contains("</testcase>"));
    }

    #[test]
    fn test_junit_formatter_warning_only_not_counted_as_failure() {
        let results = vec![ValidationResult {
            filename: "warn.yaml".to_string(),
            issues: vec![ValidationError {
                rule_id: Some("W3001".to_string()),
                message: "Some warning".to_string(),
                path: vec![],
                span: Span {
                    start: Position { line: 1, column: 1 },
                    end: Position { line: 1, column: 1 },
                },
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }],
        }];
        let out = JUnitFormatter.format(&results);
        // tests=1 but failures=0 because only a warning
        assert!(out.contains("<testsuite name=\"cfn-lint\" tests=\"1\" failures=\"0\">"));
        // The warning still appears as a <failure> element (it's a lint finding)
        assert!(out.contains("type=\"W3001\""));
    }

    #[test]
    fn test_junit_formatter_xml_escaping() {
        let results = vec![ValidationResult {
            filename: "tmpl.yaml".to_string(),
            issues: vec![ValidationError {
                rule_id: Some("E9999".to_string()),
                message: "Value <a> & \"b\" > c".to_string(),
                path: vec![],
                span: Span {
                    start: Position { line: 1, column: 1 },
                    end: Position { line: 1, column: 1 },
                },
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }],
        }];
        let out = JUnitFormatter.format(&results);
        assert!(out.contains("&lt;a&gt;"));
        assert!(out.contains("&amp;"));
        assert!(out.contains("&quot;b&quot;"));
        assert!(!out.contains("<a>"));
    }

    #[test]
    fn test_junit_formatter_apostrophes_and_control_chars() {
        // Message contains single quotes plus a mix of XML-forbidden control
        // characters (0x00, 0x08, 0x0B, 0x0C, 0x1F) and legal whitespace
        // control characters (\t, \n, \r) that must be preserved.
        let message = "It's a 'value' \u{0}\u{8}\u{b}\u{c}\u{1f}with\tctrl\nchars\r".to_string();
        let results = vec![ValidationResult {
            // Apostrophe in the filename exercises escaping in the name attr.
            filename: "it's.yaml".to_string(),
            issues: vec![ValidationError {
                rule_id: Some("E9999".to_string()),
                message,
                path: vec![],
                span: Span {
                    start: Position { line: 1, column: 1 },
                    end: Position { line: 1, column: 1 },
                },
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }],
        }];
        let out = JUnitFormatter.format(&results);

        // Single quotes are escaped as &apos;
        assert!(out.contains("It&apos;s a &apos;value&apos;"));
        assert!(out.contains("<testcase name=\"it&apos;s.yaml\">"));
        assert!(!out.contains("It's"));

        // XML-1.0-forbidden control characters are stripped entirely.
        for forbidden in ['\u{0}', '\u{8}', '\u{b}', '\u{c}', '\u{1f}'] {
            assert!(
                !out.contains(forbidden),
                "forbidden control char {:#x} should be stripped",
                forbidden as u32
            );
        }
        // Numeric-reference escapes are not used for forbidden chars either.
        assert!(!out.contains("&#0;"));
        assert!(!out.contains("&#x0;"));

        // Legal whitespace control characters survive.
        assert!(out.contains("with\tctrl\nchars\r"));

        // The full document must parse as well-formed XML. roxmltree enforces
        // XML 1.0 character-range rules, so any leaked control char fails here.
        roxmltree::Document::parse(&out).expect("JUnit output should be well-formed XML");
    }

    #[test]
    fn test_get_formatter_junit() {
        let f = get_formatter("junit");
        let out = f.format(&sample_results());
        assert!(out.contains("<testsuites>"));
        assert!(out.contains("<testsuite name=\"cfn-lint\""));
    }

    #[test]
    fn test_sarif_formatter_basic() {
        let out = SarifFormatter.format(&sample_results());
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();

        // Top-level structure
        assert_eq!(parsed["version"], "2.1.0");
        assert!(parsed["$schema"]
            .as_str()
            .unwrap()
            .contains("sarif-schema-2.1.0.json"));

        let run = &parsed["runs"][0];

        // Tool driver
        assert_eq!(run["tool"]["driver"]["name"], "cfn-lint");
        assert_eq!(run["tool"]["driver"]["version"], "2.0.0");

        // Rules — deduplicated, E1003 and W2001 both present
        let rules = run["tool"]["driver"]["rules"].as_array().unwrap();
        assert_eq!(rules.len(), 2);
        let rule_ids: Vec<&str> = rules.iter().map(|r| r["id"].as_str().unwrap()).collect();
        assert!(rule_ids.contains(&"E1003"));
        assert!(rule_ids.contains(&"W2001"));

        // Results
        let results = run["results"].as_array().unwrap();
        assert_eq!(results.len(), 2);

        // First result: E1003 → error
        let r0 = &results[0];
        assert_eq!(r0["ruleId"], "E1003");
        assert_eq!(r0["level"], "error");
        assert_eq!(r0["message"]["text"], "Description too long");
        let loc0 = &r0["locations"][0]["physicalLocation"];
        assert_eq!(loc0["artifactLocation"]["uri"], "template.yaml");
        assert_eq!(loc0["artifactLocation"]["uriBaseId"], "EXECUTIONROOT");
        assert_eq!(loc0["region"]["startLine"], 2);
        assert_eq!(loc0["region"]["startColumn"], 1);

        // Second result: W2001 → warning
        let r1 = &results[1];
        assert_eq!(r1["ruleId"], "W2001");
        assert_eq!(r1["level"], "warning");
        assert_eq!(r1["message"]["text"], "Unused parameter");
    }

    #[test]
    fn test_sarif_formatter_empty() {
        let results: Vec<ValidationResult> = vec![];
        let out = SarifFormatter.format(&results);
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(parsed["version"], "2.1.0");
        assert_eq!(parsed["runs"][0]["results"].as_array().unwrap().len(), 0);
        assert_eq!(
            parsed["runs"][0]["tool"]["driver"]["rules"]
                .as_array()
                .unwrap()
                .len(),
            0
        );
    }

    #[test]
    fn test_sarif_formatter_informational() {
        let results = vec![ValidationResult {
            filename: "t.yaml".to_string(),
            issues: vec![ValidationError {
                rule_id: Some("I1001".to_string()),
                message: "Info message".to_string(),
                path: vec![],
                span: Span {
                    start: Position { line: 1, column: 1 },
                    end: Position { line: 1, column: 1 },
                },
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }],
        }];
        let out = SarifFormatter.format(&results);
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(parsed["runs"][0]["results"][0]["level"], "note");
    }

    #[test]
    fn test_sarif_rules_deduplicated() {
        // Two issues with the same rule_id should produce only one rule entry.
        let results = vec![ValidationResult {
            filename: "t.yaml".to_string(),
            issues: vec![
                ValidationError {
                    rule_id: Some("E1003".to_string()),
                    message: "First".to_string(),
                    path: vec![],
                    span: Span {
                        start: Position { line: 1, column: 1 },
                        end: Position { line: 1, column: 1 },
                    },
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                },
                ValidationError {
                    rule_id: Some("E1003".to_string()),
                    message: "Second".to_string(),
                    path: vec![],
                    span: Span {
                        start: Position { line: 2, column: 1 },
                        end: Position { line: 2, column: 1 },
                    },
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                },
            ],
        }];
        let out = SarifFormatter.format(&results);
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        let rules = parsed["runs"][0]["tool"]["driver"]["rules"]
            .as_array()
            .unwrap();
        assert_eq!(
            rules.len(),
            1,
            "duplicate rule_id should produce one rule entry"
        );
        assert_eq!(parsed["runs"][0]["results"].as_array().unwrap().len(), 2);
    }

    #[test]
    fn test_get_formatter_sarif() {
        let f = get_formatter("sarif");
        let out = f.format(&sample_results());
        let parsed: serde_json::Value = serde_json::from_str(&out).unwrap();
        assert_eq!(parsed["version"], "2.1.0");
    }
}
