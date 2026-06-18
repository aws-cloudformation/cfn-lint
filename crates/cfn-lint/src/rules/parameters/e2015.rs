use regex::Regex;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

pub struct E2015;

impl E2015 {
    fn make_issue(&self, name: &str, default_node: &AstNode, message: &str) -> ValidationError {
        ValidationError {
            rule_id: Some(self.id().to_string()),
            message: message.to_string(),
            path: vec![
                "Parameters".to_string(),
                name.to_string(),
                "Default".to_string(),
            ],
            span: default_node.span(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
        schema_id: None,
        }
    }
}

impl CfnLintRule for E2015 {
    fn id(&self) -> &str {
        "E2015"
    }

    fn short_description(&self) -> &str {
        "Default value is within parameter constraints"
    }

    fn description(&self) -> &str {
        "Validates parameter default values satisfy all constraints (AllowedValues, AllowedPattern, min/max)"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let params = match root.get("Parameters").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        let mut issues = Vec::new();
        for (name, node) in params.iter() {
            let obj = match node.as_object() {
                Some(o) => o,
                None => continue,
            };

            // Skip if Type is a function
            let type_node = match obj.get("Type") {
                Some(n) => n,
                None => continue,
            };
            if type_node.as_function().is_some() {
                continue;
            }
            let param_type = type_node.as_str().unwrap_or("");

            let default_node = match obj.get("Default") {
                Some(n) => n,
                None => continue,
            };
            // Skip if Default is a function (e.g. !Ref)
            if default_node.as_function().is_some() {
                continue;
            }

            let default_str = match default_node.as_str() {
                Some(s) => s.to_string(),
                None => match default_node.as_f64() {
                    Some(n) => {
                        if n.fract() == 0.0 {
                            format!("{}", n as i64)
                        } else {
                            format!("{}", n)
                        }
                    }
                    None => continue,
                },
            };

            let is_cdl = param_type == "CommaDelimitedList";

            // AllowedPattern
            if let Some(pattern_str) = obj.get("AllowedPattern").and_then(|n| n.as_str()) {
                if let Ok(re) = Regex::new(&format!("^(?:{})$", pattern_str)) {
                    if is_cdl {
                        let any_fail = default_str.split(',').map(|s| s.trim()).any(|v| !re.is_match(v));
                        if any_fail {
                            issues.push(self.make_issue(name, default_node, "Default should be allowed by AllowedPattern"));
                        }
                    } else if !re.is_match(&default_str) {
                        issues.push(self.make_issue(name, default_node, "Default should be allowed by AllowedPattern"));
                    }
                }
            }

            // MinValue (Number type)
            if let Some(min_node) = obj.get("MinValue") {
                if let (Some(min_val), Some(default_val)) = (min_node.as_f64(), default_node.as_f64()) {
                    if (default_val as i64) < (min_val as i64) {
                        issues.push(self.make_issue(name, default_node, "Default should be equal to or higher than MinValue"));
                    }
                }
            }

            // MaxValue (Number type)
            if let Some(max_node) = obj.get("MaxValue") {
                if let (Some(max_val), Some(default_val)) = (max_node.as_f64(), default_node.as_f64()) {
                    if (default_val as i64) > (max_val as i64) {
                        issues.push(self.make_issue(name, default_node, "Default should be less than or equal to MaxValue"));
                    }
                }
            }

            // AllowedValues
            if let Some(av_node) = obj.get("AllowedValues") {
                if let Some(arr) = av_node.as_array() {
                    let allowed: Vec<String> = arr.elements.iter().filter_map(|e| {
                        e.as_str().map(|s| s.to_string()).or_else(|| {
                            e.as_f64().map(|n| if n.fract() == 0.0 { format!("{}", n as i64) } else { format!("{}", n) })
                        })
                    }).collect();
                    if is_cdl {
                        // Python logic: for CDL, split and check each value.
                        // If split check fails, also check whole string.
                        // Only report if whole-string check also fails.
                        let split_fail = default_str.split(',').map(|s| s.trim())
                            .any(|v| !allowed.iter().any(|a| a == v));
                        if split_fail {
                            let whole_fail = !allowed.iter().any(|v| v == &default_str);
                            if whole_fail {
                                issues.push(self.make_issue(name, default_node, "Default should be a value within AllowedValues"));
                            }
                        }
                    } else if !allowed.iter().any(|v| v == &default_str) {
                        issues.push(self.make_issue(name, default_node, "Default should be a value within AllowedValues"));
                    }
                }
            }

            // MinLength
            if let Some(ml_node) = obj.get("MinLength") {
                if let Some(min_len) = ml_node.as_f64() {
                    if (default_str.len() as f64) < min_len {
                        issues.push(self.make_issue(name, default_node, "Default should have a length above or equal to MinLength"));
                    }
                }
            }

            // MaxLength
            if let Some(ml_node) = obj.get("MaxLength") {
                if let Some(max_len) = ml_node.as_f64() {
                    if (default_str.len() as f64) > max_len {
                        issues.push(self.make_issue(name, default_node, "Default should have a length below or equal to MaxLength"));
                    }
                }
            }
        }
        issues
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_default_matches_pattern() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
    Default: prod
    AllowedPattern: "[a-z]+"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E2015.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_default_does_not_match_pattern() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
    Default: PROD123
    AllowedPattern: "[a-z]+"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E2015.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E2015"));
        assert_eq!(issues[0].message, "Default should be allowed by AllowedPattern");
    }

    #[test]
    fn test_no_pattern_no_issue() {
        let yaml = br#"
Parameters:
  Env:
    Type: String
    Default: anything
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E2015.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E2015);
