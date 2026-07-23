use std::path::Path;
use std::sync::Arc;

use regex::Regex;
use thiserror::Error;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

#[derive(Debug, Error)]
pub enum CustomRuleError {
    #[error("Failed to read custom rules file: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Line {line}: {message}")]
    ParseError { line: usize, message: String },
    #[error("Line {line}: invalid regex '{pattern}': {source}")]
    RegexError {
        line: usize,
        pattern: String,
        source: regex::Error,
    },
}

#[derive(Debug, Clone)]
pub enum Operator {
    Equals(String),
    NotEquals(String),
    In(Vec<String>),
    NotIn(Vec<String>),
    RegexMatch(Regex),
    IsDefined,
    NotDefined,
    GreaterThan(f64),
    GreaterThanOrEqual(f64),
    LessThan(f64),
    LessThanOrEqual(f64),
}

#[derive(Debug, Clone)]
pub struct CustomRule {
    id: String,
    resource_type: String,
    property: String,
    operator: Operator,
    severity: Severity,
    custom_message: Option<String>,
    raw_line: String,
}

impl CfnLintRule for CustomRule {
    fn id(&self) -> &str {
        &self.id
    }

    fn short_description(&self) -> &str {
        match &self.custom_message {
            Some(msg) => msg,
            None => &self.raw_line,
        }
    }

    fn description(&self) -> &str {
        &self.raw_line
    }

    fn severity(&self) -> Severity {
        self.severity
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, _root: &AstNode) -> Vec<ValidationError> {
        let mut issues = Vec::new();
        for (name, resource) in &template.resources {
            if resource.resource_type != self.resource_type {
                continue;
            }
            let prop_value = resource
                .properties
                .as_ref()
                .and_then(|p| get_nested(p, &self.property));

            let mut path = vec![
                "Resources".to_string(),
                name.clone(),
                "Properties".to_string(),
            ];
            path.extend(self.property.split('.').map(|s| s.to_string()));
            let pos = prop_value
                .map(|v| v.span())
                .or_else(|| resource.properties.as_ref().map(|p| p.span()))
                .unwrap_or_default();

            let violation = match &self.operator {
                Operator::IsDefined => prop_value.is_none(),
                Operator::NotDefined => prop_value.is_some(),
                Operator::Equals(expected) => match prop_value.and_then(|v| v.as_str()) {
                    Some(s) => s != expected,
                    None => true,
                },
                Operator::NotEquals(expected) => match prop_value.and_then(|v| v.as_str()) {
                    Some(s) => s == expected,
                    None => false,
                },
                Operator::In(values) => match prop_value.and_then(|v| v.as_str()) {
                    Some(s) => !values.iter().any(|v| v == s),
                    None => true,
                },
                Operator::NotIn(values) => match prop_value.and_then(|v| v.as_str()) {
                    Some(s) => values.iter().any(|v| v == s),
                    None => false,
                },
                Operator::RegexMatch(re) => match prop_value.and_then(|v| v.as_str()) {
                    Some(s) => !re.is_match(s),
                    None => true,
                },
                Operator::GreaterThan(threshold) => match prop_value.and_then(|v| v.as_f64()) {
                    Some(n) => {
                        !matches!(n.partial_cmp(threshold), Some(std::cmp::Ordering::Greater))
                    }
                    None => true,
                },
                Operator::GreaterThanOrEqual(threshold) => {
                    match prop_value.and_then(|v| v.as_f64()) {
                        Some(n) => !matches!(
                            n.partial_cmp(threshold),
                            Some(std::cmp::Ordering::Greater | std::cmp::Ordering::Equal)
                        ),
                        None => true,
                    }
                }
                Operator::LessThan(threshold) => match prop_value.and_then(|v| v.as_f64()) {
                    Some(n) => !matches!(n.partial_cmp(threshold), Some(std::cmp::Ordering::Less)),
                    None => true,
                },
                Operator::LessThanOrEqual(threshold) => match prop_value.and_then(|v| v.as_f64()) {
                    Some(n) => !matches!(
                        n.partial_cmp(threshold),
                        Some(std::cmp::Ordering::Less | std::cmp::Ordering::Equal)
                    ),
                    None => true,
                },
            };

            if violation {
                let message = match &self.custom_message {
                    Some(msg) => msg.clone(),
                    None => format!("Custom rule violation: {}", self.raw_line),
                };
                issues.push(ValidationError {
                    rule_id: Some(self.id.clone()),
                    message,
                    path,
                    span: pos,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
            }
        }
        issues
    }
}

/// Parse a custom rules text file and return CfnLintRule trait objects.
pub fn load_custom_rules(path: &Path) -> Result<Vec<Arc<dyn CfnLintRule>>, CustomRuleError> {
    let content = std::fs::read_to_string(path)?;
    parse_custom_rules(&content)
}

/// Resolve a (possibly dotted) property path against a node (C54).
///
/// Each `.`-separated segment is resolved either as an object key or, when the
/// current node is an array and the segment parses as an index, as an array
/// index. A plain (dot-free) property behaves exactly like a single object
/// lookup, so existing rules are unaffected.
fn get_nested<'a>(node: &'a AstNode, property: &str) -> Option<&'a AstNode> {
    let mut current = node;
    for segment in property.split('.') {
        current = match current {
            AstNode::Array(arr) => {
                let idx: usize = segment.parse().ok()?;
                arr.elements.get(idx)?
            }
            _ => current.get(segment)?,
        };
    }
    Some(current)
}

/// Extract a quoted string from the end of the remaining text.
/// Returns (remaining_text_before_quote, extracted_message).
fn extract_quoted_message(text: &str) -> (String, Option<String>) {
    let trimmed = text.trim_end();
    if let Some(stripped) = trimmed.strip_suffix('"') {
        // Find the opening quote (scan backwards from the closing quote)
        if let Some(open_idx) = stripped.rfind('"') {
            let message = stripped[open_idx + 1..].to_string();
            let before = trimmed[..open_idx].trim_end().to_string();
            return (before, Some(message));
        }
    }
    (trimmed.to_string(), None)
}

/// Split the text following an operator into its value and an optional
/// trailing severity keyword.
///
/// Severity (`WARN`/`ERROR`) is only recognised as a *standalone trailing
/// token that follows a value* (C55). This prevents a value that legitimately
/// equals "ERROR"/"WARN" (e.g. `Tag EQUALS ERROR`) from being misparsed as an
/// empty value with that severity.
///
/// For operators that take no value (`IS_DEFINED`/`NOT_DEFINED`), a lone
/// `WARN`/`ERROR` token is treated as the severity.
fn split_value_severity(rest: &str, takes_value: bool) -> (String, Severity) {
    let rest = rest.trim();

    if !takes_value {
        return match rest {
            "WARN" => (String::new(), Severity::Warning),
            "ERROR" => (String::new(), Severity::Error),
            _ => (rest.to_string(), Severity::Error),
        };
    }

    let tokens: Vec<&str> = rest.split_whitespace().collect();
    // Only strip a trailing severity token when a value precedes it.
    if tokens.len() >= 2 {
        let last = tokens[tokens.len() - 1];
        if last == "WARN" || last == "ERROR" {
            let severity = if last == "WARN" {
                Severity::Warning
            } else {
                Severity::Error
            };
            // Remove the trailing severity token (its last occurrence).
            let cut = rest.rfind(last).unwrap_or(rest.len());
            let value = rest[..cut].trim_end().to_string();
            return (value, severity);
        }
    }

    (rest.to_string(), Severity::Error)
}

fn parse_custom_rules(content: &str) -> Result<Vec<Arc<dyn CfnLintRule>>, CustomRuleError> {
    let mut rules: Vec<Arc<dyn CfnLintRule>> = Vec::new();
    let mut index = 1u32;

    for (line_num, line) in content.lines().enumerate() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        // First extract the optional quoted message from the end
        let (after_msg, custom_message) = extract_quoted_message(line);

        // Now parse the core: ResourceType Property Operator [Value] [Severity]
        let core = after_msg.trim();
        let parts: Vec<&str> = core.splitn(4, ' ').collect();
        if parts.len() < 3 {
            return Err(CustomRuleError::ParseError {
                line: line_num + 1,
                message: format!(
                    "expected at least 'ResourceType Property Operator', got: {}",
                    line
                ),
            });
        }

        let resource_type = parts[0].to_string();
        let property = parts[1].to_string();
        let op_str = parts[2];
        let rest = parts.get(3).copied().unwrap_or("").trim();

        // Severity is only a trailing token after the value, so it must be
        // split with knowledge of whether the operator expects a value.
        let takes_value = !matches!(op_str, "IS_DEFINED" | "NOT_DEFINED");
        let (value_owned, severity) = split_value_severity(rest, takes_value);
        let value_str = value_owned.as_str();

        let operator = match op_str {
            "IS_DEFINED" => Operator::IsDefined,
            "NOT_DEFINED" => Operator::NotDefined,
            "EQUALS" | "==" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: "EQUALS requires a value".to_string(),
                    });
                }
                Operator::Equals(value_str.to_string())
            }
            "NOT_EQUALS" | "!=" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: "NOT_EQUALS requires a value".to_string(),
                    });
                }
                Operator::NotEquals(value_str.to_string())
            }
            "IN" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: "IN requires comma-separated values".to_string(),
                    });
                }
                Operator::In(value_str.split(',').map(|s| s.trim().to_string()).collect())
            }
            "NOT_IN" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: "NOT_IN requires comma-separated values".to_string(),
                    });
                }
                Operator::NotIn(value_str.split(',').map(|s| s.trim().to_string()).collect())
            }
            "REGEX_MATCH" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: "REGEX_MATCH requires a pattern".to_string(),
                    });
                }
                let re = Regex::new(value_str).map_err(|e| CustomRuleError::RegexError {
                    line: line_num + 1,
                    pattern: value_str.to_string(),
                    source: e,
                })?;
                Operator::RegexMatch(re)
            }
            ">" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: "> requires a numeric value".to_string(),
                    });
                }
                let n = value_str
                    .parse::<f64>()
                    .map_err(|_| CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: format!("> requires a numeric value, got '{}'", value_str),
                    })?;
                Operator::GreaterThan(n)
            }
            ">=" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: ">= requires a numeric value".to_string(),
                    });
                }
                let n = value_str
                    .parse::<f64>()
                    .map_err(|_| CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: format!(">= requires a numeric value, got '{}'", value_str),
                    })?;
                Operator::GreaterThanOrEqual(n)
            }
            "<" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: "< requires a numeric value".to_string(),
                    });
                }
                let n = value_str
                    .parse::<f64>()
                    .map_err(|_| CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: format!("< requires a numeric value, got '{}'", value_str),
                    })?;
                Operator::LessThan(n)
            }
            "<=" => {
                if value_str.is_empty() {
                    return Err(CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: "<= requires a numeric value".to_string(),
                    });
                }
                let n = value_str
                    .parse::<f64>()
                    .map_err(|_| CustomRuleError::ParseError {
                        line: line_num + 1,
                        message: format!("<= requires a numeric value, got '{}'", value_str),
                    })?;
                Operator::LessThanOrEqual(n)
            }
            other => {
                return Err(CustomRuleError::ParseError {
                    line: line_num + 1,
                    message: format!(
                        "unknown operator '{}', expected one of: EQUALS, ==, NOT_EQUALS, !=, IN, NOT_IN, REGEX_MATCH, IS_DEFINED, NOT_DEFINED, >, >=, <, <=",
                        other
                    ),
                });
            }
        };

        let id = format!("E9{:03}", index);
        index += 1;

        rules.push(Arc::new(CustomRule {
            id,
            resource_type,
            property,
            operator,
            severity,
            custom_message,
            raw_line: line.to_string(),
        }));
    }

    Ok(rules)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::ast::{NumberNode, ObjectEntry, ObjectNode, Position, Span, StringNode};
    use crate::template::Template;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn make_template(resource_type: &str, props: Vec<(&str, &str)>) -> (Template, AstNode) {
        let mut prop_map: Vec<ObjectEntry> = Vec::new();
        for (k, v) in props {
            prop_map.push(ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: k.to_string(),
                    span: Span::default(),
                }),
                key: k.to_string(),
                value: AstNode::String(StringNode {
                    value: v.to_string(),
                    span: Span {
                        start: Position { line: 5, column: 3 },
                        end: Position { line: 5, column: 3 },
                    },
                }),
                key_span: Span::default(),
            });
        }
        let res_inner: Vec<ObjectEntry> = vec![
            ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: "Type".to_string(),
                    span: Span::default(),
                }),
                key: "Type".to_string(),
                value: AstNode::String(StringNode {
                    value: resource_type.to_string(),
                    span: Span::default(),
                }),
                key_span: Span::default(),
            },
            ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: "Properties".to_string(),
                    span: Span::default(),
                }),
                key: "Properties".to_string(),
                value: AstNode::Object(ObjectNode {
                    entries: prop_map,
                    span: Span::default(),
                }),
                key_span: Span::default(),
            },
        ];
        let resources: Vec<ObjectEntry> = vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "MyResource".to_string(),
                span: Span::default(),
            }),
            key: "MyResource".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: res_inner,
                span: Span::default(),
            }),
            key_span: Span::default(),
        }];
        let root_props: Vec<ObjectEntry> = vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "Resources".to_string(),
                span: Span::default(),
            }),
            key: "Resources".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: resources,
                span: Span::default(),
            }),
            key_span: Span::default(),
        }];
        let root = AstNode::Object(ObjectNode {
            entries: root_props,
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        (tmpl, root)
    }

    // --- Parsing tests ---

    #[test]
    fn test_parse_is_defined() {
        let rules = parse_custom_rules("AWS::S3::Bucket BucketEncryption IS_DEFINED\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].id(), "E9001");
        assert_eq!(rules[0].severity(), Severity::Error);
    }

    #[test]
    fn test_parse_not_defined() {
        let rules = parse_custom_rules("AWS::S3::Bucket PublicAccess NOT_DEFINED\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].id(), "E9001");
    }

    #[test]
    fn test_parse_equals() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance InstanceType EQUALS t3.micro\n").unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_not_equals() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance InstanceType NOT_EQUALS t2.micro\n").unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_in() {
        let rules = parse_custom_rules(
            "AWS::Lambda::Function Runtime IN nodejs20.x,python3.12,python3.13\n",
        )
        .unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_not_in() {
        let rules =
            parse_custom_rules("AWS::Lambda::Function Runtime NOT_IN python2.7,python3.6\n")
                .unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_regex_match() {
        let rules =
            parse_custom_rules("AWS::S3::Bucket BucketName REGEX_MATCH ^my-company-.*\n").unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_multiple_rules() {
        let content = "\
AWS::S3::Bucket BucketEncryption IS_DEFINED
AWS::Lambda::Function Runtime IN nodejs20.x,python3.12
AWS::EC2::Instance InstanceType NOT_EQUALS t2.micro
";
        let rules = parse_custom_rules(content).unwrap();
        assert_eq!(rules.len(), 3);
        assert_eq!(rules[0].id(), "E9001");
        assert_eq!(rules[1].id(), "E9002");
        assert_eq!(rules[2].id(), "E9003");
    }

    #[test]
    fn test_parse_skips_comments_and_blank_lines() {
        let content = "\
# This is a comment
AWS::S3::Bucket BucketEncryption IS_DEFINED

# Another comment
AWS::Lambda::Function Runtime IN nodejs20.x
";
        let rules = parse_custom_rules(content).unwrap();
        assert_eq!(rules.len(), 2);
    }

    #[test]
    fn test_parse_error_too_few_parts() {
        let result = parse_custom_rules("AWS::S3::Bucket\n");
        assert!(result.is_err());
        let err = result.err().unwrap();
        assert!(err.to_string().contains("Line 1"));
    }

    #[test]
    fn test_parse_error_unknown_operator() {
        let result = parse_custom_rules("AWS::S3::Bucket Prop FOOBAR value\n");
        assert!(result.is_err());
        assert!(result
            .err()
            .unwrap()
            .to_string()
            .contains("unknown operator"));
    }

    #[test]
    fn test_parse_error_equals_missing_value() {
        let result = parse_custom_rules("AWS::S3::Bucket Prop EQUALS\n");
        assert!(result.is_err());
        assert!(result
            .err()
            .unwrap()
            .to_string()
            .contains("EQUALS requires a value"));
    }

    #[test]
    fn test_parse_error_invalid_regex() {
        let result = parse_custom_rules("AWS::S3::Bucket Prop REGEX_MATCH [invalid\n");
        assert!(result.is_err());
        assert!(result.err().unwrap().to_string().contains("invalid regex"));
    }

    // --- Validation tests ---

    #[test]
    fn test_validate_is_defined_pass() {
        let rules = parse_custom_rules("AWS::S3::Bucket BucketName IS_DEFINED\n").unwrap();
        let (tmpl, root) = make_template("AWS::S3::Bucket", vec![("BucketName", "my-bucket")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_is_defined_fail() {
        let rules = parse_custom_rules("AWS::S3::Bucket BucketEncryption IS_DEFINED\n").unwrap();
        let (tmpl, root) = make_template("AWS::S3::Bucket", vec![("BucketName", "my-bucket")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E9001"));
        assert!(issues[0].message.contains("Custom rule violation"));
    }

    #[test]
    fn test_validate_not_defined_pass() {
        let rules = parse_custom_rules("AWS::S3::Bucket BadProp NOT_DEFINED\n").unwrap();
        let (tmpl, root) = make_template("AWS::S3::Bucket", vec![("BucketName", "my-bucket")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_not_defined_fail() {
        let rules = parse_custom_rules("AWS::S3::Bucket BucketName NOT_DEFINED\n").unwrap();
        let (tmpl, root) = make_template("AWS::S3::Bucket", vec![("BucketName", "my-bucket")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_equals_pass() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance InstanceType EQUALS t3.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t3.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_equals_fail() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance InstanceType EQUALS t3.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t2.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_not_equals_pass() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance InstanceType NOT_EQUALS t2.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t3.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_not_equals_fail() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance InstanceType NOT_EQUALS t2.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t2.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_in_pass() {
        let rules = parse_custom_rules(
            "AWS::Lambda::Function Runtime IN nodejs20.x,python3.12,python3.13\n",
        )
        .unwrap();
        let (tmpl, root) = make_template("AWS::Lambda::Function", vec![("Runtime", "python3.12")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_in_fail() {
        let rules = parse_custom_rules(
            "AWS::Lambda::Function Runtime IN nodejs20.x,python3.12,python3.13\n",
        )
        .unwrap();
        let (tmpl, root) = make_template("AWS::Lambda::Function", vec![("Runtime", "python2.7")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_not_in_pass() {
        let rules =
            parse_custom_rules("AWS::Lambda::Function Runtime NOT_IN python2.7,python3.6\n")
                .unwrap();
        let (tmpl, root) = make_template("AWS::Lambda::Function", vec![("Runtime", "python3.12")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_not_in_fail() {
        let rules =
            parse_custom_rules("AWS::Lambda::Function Runtime NOT_IN python2.7,python3.6\n")
                .unwrap();
        let (tmpl, root) = make_template("AWS::Lambda::Function", vec![("Runtime", "python2.7")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_regex_match_pass() {
        let rules =
            parse_custom_rules("AWS::S3::Bucket BucketName REGEX_MATCH ^my-company-.*\n").unwrap();
        let (tmpl, root) =
            make_template("AWS::S3::Bucket", vec![("BucketName", "my-company-data")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_regex_match_fail() {
        let rules =
            parse_custom_rules("AWS::S3::Bucket BucketName REGEX_MATCH ^my-company-.*\n").unwrap();
        let (tmpl, root) = make_template("AWS::S3::Bucket", vec![("BucketName", "other-bucket")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_skips_non_matching_resource_type() {
        let rules = parse_custom_rules("AWS::S3::Bucket BucketName IS_DEFINED\n").unwrap();
        let (tmpl, root) = make_template("AWS::Lambda::Function", vec![("Runtime", "python3.12")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_issue_path() {
        let rules = parse_custom_rules("AWS::S3::Bucket BucketEncryption IS_DEFINED\n").unwrap();
        let (tmpl, root) = make_template("AWS::S3::Bucket", vec![("BucketName", "test")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert_eq!(
            issues[0].path,
            vec!["Resources", "MyResource", "Properties", "BucketEncryption"]
        );
    }

    #[test]
    fn test_load_custom_rules_from_file() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "AWS::S3::Bucket BucketEncryption IS_DEFINED").unwrap();
        writeln!(
            file,
            "AWS::Lambda::Function Runtime IN nodejs20.x,python3.12"
        )
        .unwrap();

        let rules = load_custom_rules(file.path()).unwrap();
        assert_eq!(rules.len(), 2);
        assert_eq!(rules[0].id(), "E9001");
        assert_eq!(rules[1].id(), "E9002");
    }

    #[test]
    fn test_load_custom_rules_file_not_found() {
        let result = load_custom_rules(Path::new("/nonexistent/rules.txt"));
        assert!(result.is_err());
    }

    // --- Helper for numeric templates ---

    fn make_numeric_template(
        resource_type: &str,
        prop_name: &str,
        value: f64,
    ) -> (Template, AstNode) {
        let prop_map: Vec<ObjectEntry> = vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: prop_name.to_string(),
                span: Span::default(),
            }),
            key: prop_name.to_string(),
            value: AstNode::Number(NumberNode {
                value,
                span: Span {
                    start: Position { line: 5, column: 3 },
                    end: Position { line: 5, column: 3 },
                },
            }),
            key_span: Span::default(),
        }];
        let res_inner: Vec<ObjectEntry> = vec![
            ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: "Type".to_string(),
                    span: Span::default(),
                }),
                key: "Type".to_string(),
                value: AstNode::String(StringNode {
                    value: resource_type.to_string(),
                    span: Span::default(),
                }),
                key_span: Span::default(),
            },
            ObjectEntry {
                key_node: AstNode::String(StringNode {
                    value: "Properties".to_string(),
                    span: Span::default(),
                }),
                key: "Properties".to_string(),
                value: AstNode::Object(ObjectNode {
                    entries: prop_map,
                    span: Span::default(),
                }),
                key_span: Span::default(),
            },
        ];
        let resources: Vec<ObjectEntry> = vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "MyResource".to_string(),
                span: Span::default(),
            }),
            key: "MyResource".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: res_inner,
                span: Span::default(),
            }),
            key_span: Span::default(),
        }];
        let root_props: Vec<ObjectEntry> = vec![ObjectEntry {
            key_node: AstNode::String(StringNode {
                value: "Resources".to_string(),
                span: Span::default(),
            }),
            key: "Resources".to_string(),
            value: AstNode::Object(ObjectNode {
                entries: resources,
                span: Span::default(),
            }),
            key_span: Span::default(),
        }];
        let root = AstNode::Object(ObjectNode {
            entries: root_props,
            span: Span::default(),
        });
        let tmpl = Template::from_ast(&root).unwrap();
        (tmpl, root)
    }

    // --- Parsing tests for new operators ---

    #[test]
    fn test_parse_greater_than() {
        let rules = parse_custom_rules("AWS::SQS::Queue DelaySeconds > 60\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].id(), "E9001");
    }

    #[test]
    fn test_parse_greater_than_or_equal() {
        let rules = parse_custom_rules("AWS::SQS::Queue DelaySeconds >= 10\n").unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_less_than() {
        let rules = parse_custom_rules("AWS::SQS::Queue MaximumMessageSize < 262144\n").unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_less_than_or_equal() {
        let rules = parse_custom_rules("AWS::SQS::Queue MaximumMessageSize <= 262144\n").unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_equals_alias() {
        let rules = parse_custom_rules("AWS::EC2::Instance InstanceType == t3.micro\n").unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_not_equals_alias() {
        let rules = parse_custom_rules("AWS::EC2::Instance InstanceType != t2.micro\n").unwrap();
        assert_eq!(rules.len(), 1);
    }

    #[test]
    fn test_parse_error_numeric_operator_non_numeric_value() {
        let result = parse_custom_rules("AWS::SQS::Queue DelaySeconds > abc\n");
        assert!(result.is_err());
        assert!(result.err().unwrap().to_string().contains("numeric value"));
    }

    #[test]
    fn test_parse_error_numeric_operator_missing_value() {
        let result = parse_custom_rules("AWS::SQS::Queue DelaySeconds >\n");
        assert!(result.is_err());
        assert!(result.err().unwrap().to_string().contains("numeric value"));
    }

    // --- Severity parsing tests ---

    #[test]
    fn test_parse_severity_warn() {
        let rules =
            parse_custom_rules("AWS::S3::Bucket BucketEncryption IS_DEFINED WARN\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Warning);
    }

    #[test]
    fn test_parse_severity_error_explicit() {
        let rules =
            parse_custom_rules("AWS::S3::Bucket BucketEncryption IS_DEFINED ERROR\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Error);
    }

    #[test]
    fn test_parse_severity_default_is_error() {
        let rules = parse_custom_rules("AWS::S3::Bucket BucketEncryption IS_DEFINED\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Error);
    }

    #[test]
    fn test_parse_severity_with_value() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance InstanceType EQUALS t3.micro WARN\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Warning);
    }

    #[test]
    fn test_parse_severity_numeric_with_warn() {
        let rules = parse_custom_rules("AWS::SQS::Queue DelaySeconds > 60 WARN\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Warning);
    }

    // --- Custom message parsing tests ---

    #[test]
    fn test_parse_custom_message() {
        let rules = parse_custom_rules(
            "AWS::EC2::Instance InstanceType != t2.micro ERROR \"t2.micro is deprecated\"\n",
        )
        .unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].short_description(), "t2.micro is deprecated");
        assert_eq!(rules[0].severity(), Severity::Error);
    }

    #[test]
    fn test_parse_custom_message_with_warn() {
        let rules = parse_custom_rules(
            "AWS::SQS::Queue DelaySeconds > 60 WARN \"Delay is unusually high\"\n",
        )
        .unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Warning);
        assert_eq!(rules[0].short_description(), "Delay is unusually high");
    }

    #[test]
    fn test_parse_custom_message_without_severity() {
        let rules = parse_custom_rules(
            "AWS::SQS::Queue MaximumMessageSize <= 262144 \"Max message size must be at most 256KB\"\n",
        )
        .unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Error);
        assert_eq!(
            rules[0].short_description(),
            "Max message size must be at most 256KB"
        );
    }

    #[test]
    fn test_parse_no_custom_message_uses_raw_line() {
        let rules = parse_custom_rules("AWS::S3::Bucket BucketEncryption IS_DEFINED\n").unwrap();
        assert_eq!(
            rules[0].short_description(),
            "AWS::S3::Bucket BucketEncryption IS_DEFINED"
        );
    }

    // --- Validation tests for numeric operators ---

    #[test]
    fn test_validate_greater_than_pass() {
        let rules = parse_custom_rules("AWS::SQS::Queue DelaySeconds > 60\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "DelaySeconds", 90.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_greater_than_fail_equal() {
        let rules = parse_custom_rules("AWS::SQS::Queue DelaySeconds > 60\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "DelaySeconds", 60.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_greater_than_fail_less() {
        let rules = parse_custom_rules("AWS::SQS::Queue DelaySeconds > 60\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "DelaySeconds", 30.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_greater_than_or_equal_pass() {
        let rules = parse_custom_rules("AWS::SQS::Queue DelaySeconds >= 60\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "DelaySeconds", 60.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_greater_than_or_equal_fail() {
        let rules = parse_custom_rules("AWS::SQS::Queue DelaySeconds >= 60\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "DelaySeconds", 59.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_less_than_pass() {
        let rules = parse_custom_rules("AWS::SQS::Queue MaximumMessageSize < 262144\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "MaximumMessageSize", 1024.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_less_than_fail_equal() {
        let rules = parse_custom_rules("AWS::SQS::Queue MaximumMessageSize < 262144\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "MaximumMessageSize", 262144.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_less_than_or_equal_pass() {
        let rules = parse_custom_rules("AWS::SQS::Queue MaximumMessageSize <= 262144\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "MaximumMessageSize", 262144.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_less_than_or_equal_fail() {
        let rules = parse_custom_rules("AWS::SQS::Queue MaximumMessageSize <= 262144\n").unwrap();
        let (tmpl, root) = make_numeric_template("AWS::SQS::Queue", "MaximumMessageSize", 300000.0);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    // --- Validation tests for aliases ---

    #[test]
    fn test_validate_equals_alias_pass() {
        let rules = parse_custom_rules("AWS::EC2::Instance InstanceType == t3.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t3.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_equals_alias_fail() {
        let rules = parse_custom_rules("AWS::EC2::Instance InstanceType == t3.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t2.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_validate_not_equals_alias_pass() {
        let rules = parse_custom_rules("AWS::EC2::Instance InstanceType != t2.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t3.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_validate_not_equals_alias_fail() {
        let rules = parse_custom_rules("AWS::EC2::Instance InstanceType != t2.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t2.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
    }

    // --- Validation test for custom message ---

    #[test]
    fn test_validate_custom_message_in_error() {
        let rules = parse_custom_rules(
            "AWS::EC2::Instance InstanceType != t2.micro ERROR \"t2.micro is deprecated\"\n",
        )
        .unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t2.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].message, "t2.micro is deprecated");
    }

    #[test]
    fn test_validate_no_custom_message_uses_default() {
        let rules = parse_custom_rules("AWS::EC2::Instance InstanceType != t2.micro\n").unwrap();
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("InstanceType", "t2.micro")]);
        let issues = rules[0].validate_template(&tmpl, &root);
        assert_eq!(issues.len(), 1);
        assert!(issues[0].message.starts_with("Custom rule violation:"));
    }

    // --- Complex scenario tests ---

    #[test]
    fn test_parse_complex_rules_file() {
        let content = "\
# Numeric comparisons
AWS::SQS::Queue DelaySeconds > 60 WARN \"Delay is unusually high\"
AWS::SQS::Queue MaximumMessageSize <= 262144

# Aliases
AWS::EC2::Instance InstanceType != t2.micro ERROR \"t2.micro is deprecated\"

# Just severity, no message
AWS::S3::Bucket BucketEncryption IS_DEFINED WARN
";
        let rules = parse_custom_rules(content).unwrap();
        assert_eq!(rules.len(), 4);
        assert_eq!(rules[0].severity(), Severity::Warning);
        assert_eq!(rules[0].short_description(), "Delay is unusually high");
        assert_eq!(rules[1].severity(), Severity::Error);
        assert_eq!(rules[2].severity(), Severity::Error);
        assert_eq!(rules[2].short_description(), "t2.micro is deprecated");
        assert_eq!(rules[3].severity(), Severity::Warning);
    }

    // --- C55: value ending in a severity keyword ---

    #[test]
    fn test_parse_value_equals_error_keyword() {
        // "ERROR" here is the VALUE, not a severity keyword.
        let rules = parse_custom_rules("AWS::EC2::Instance Tag EQUALS ERROR\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Error);
        // The value must be "ERROR": a resource whose Tag == ERROR passes.
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("Tag", "ERROR")]);
        assert!(rules[0].validate_template(&tmpl, &root).is_empty());
        // A resource whose Tag != ERROR violates.
        let (tmpl2, root2) = make_template("AWS::EC2::Instance", vec![("Tag", "other")]);
        assert_eq!(rules[0].validate_template(&tmpl2, &root2).len(), 1);
    }

    #[test]
    fn test_parse_value_equals_warn_keyword() {
        let rules = parse_custom_rules("AWS::EC2::Instance Tag EQUALS WARN\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Error);
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("Tag", "WARN")]);
        assert!(rules[0].validate_template(&tmpl, &root).is_empty());
    }

    #[test]
    fn test_parse_value_then_trailing_severity_still_works() {
        // Value "foo" followed by a real trailing severity token.
        let rules = parse_custom_rules("AWS::EC2::Instance Tag EQUALS foo WARN\n").unwrap();
        assert_eq!(rules.len(), 1);
        assert_eq!(rules[0].severity(), Severity::Warning);
        let (tmpl, root) = make_template("AWS::EC2::Instance", vec![("Tag", "foo")]);
        assert!(rules[0].validate_template(&tmpl, &root).is_empty());
        let (tmpl2, root2) = make_template("AWS::EC2::Instance", vec![("Tag", "bar")]);
        assert_eq!(rules[0].validate_template(&tmpl2, &root2).len(), 1);
    }

    // --- C54: dotted property paths ---

    #[test]
    fn test_dotted_property_is_defined_resolves() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance NetworkInterfaces.0.SubnetId IS_DEFINED\n")
                .unwrap();
        let yaml = br#"
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      NetworkInterfaces:
        - DeviceIndex: "0"
          SubnetId: subnet-123
"#;
        let ast = crate::parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        // The dotted path resolves to a defined value -> no violation.
        assert!(rules[0].validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_dotted_property_missing_reports_violation_with_segmented_path() {
        let rules =
            parse_custom_rules("AWS::EC2::Instance NetworkInterfaces.0.PrivateIp IS_DEFINED\n")
                .unwrap();
        let yaml = br#"
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      NetworkInterfaces:
        - DeviceIndex: "0"
          SubnetId: subnet-123
"#;
        let ast = crate::parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = rules[0].validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1, "got: {:?}", issues);
        assert_eq!(
            issues[0].path,
            vec![
                "Resources",
                "Instance",
                "Properties",
                "NetworkInterfaces",
                "0",
                "PrivateIp"
            ]
        );
    }

    #[test]
    fn test_get_nested_plain_property_backwards_compatible() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: my-bucket
"#;
        let ast = crate::parser::parse(yaml).unwrap();
        let props = ast
            .get("Resources")
            .unwrap()
            .get("Bucket")
            .unwrap()
            .get("Properties")
            .unwrap();
        assert_eq!(
            get_nested(props, "BucketName").and_then(|n| n.as_str()),
            Some("my-bucket")
        );
        assert!(get_nested(props, "Missing").is_none());
    }
}
