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
}
