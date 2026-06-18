use regex::Regex;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// W1020: Fn::Sub isn't needed if it doesn't have a variable defined.
pub struct W1020;

impl CfnLintRule for W1020 {
    fn id(&self) -> &str {
        "W1020"
    }
    fn short_description(&self) -> &str {
        "Sub isn't needed if it doesn't have a variable defined"
    }
    fn description(&self) -> &str {
        "Checks Fn::Sub strings to see if a variable is defined."
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        if crate::transform::is_sam_template(root) {
            return vec![];
        }
        let re = Regex::new(r"\$\{\s*[^!\s].*?\s*\}").unwrap();
        let mut issues = Vec::new();
        find_sub_no_vars(root, &[], &re, &mut issues);
        issues
    }
}

fn find_sub_no_vars(
    node: &AstNode,
    path: &[String],
    re: &Regex,
    issues: &mut Vec<ValidationError>,
) {
    match node {
        AstNode::Function(func) => {
            if func.name == "Fn::Sub" {
                let template_str = match func.args.as_ref() {
                    AstNode::String(s) => Some(s.value.as_str()),
                    AstNode::Array(arr) if !arr.elements.is_empty() => arr.elements[0].as_str(),
                    _ => None,
                };
                if let Some(s) = template_str {
                    if !re.is_match(s) {
                        issues.push(ValidationError {
                            rule_id: Some("W1020".to_string()),
                            message: "'Fn::Sub' isn't needed because there are no variables"
                                .to_string(),
                            path: path.to_vec(),
                            span: func.span.clone(),
                            keyword: String::new(),
                            unknown: false,
                            resolved_from_ref: false,
                            context: vec![],
                            schema_id: None,
                        });
                    }
                }
                return; // don't descend into Fn::Sub args
            }
            find_sub_no_vars(&func.args, path, re, issues);
        }
        AstNode::Object(obj) => {
            for (key, val) in obj.iter() {
                let mut child_path = path.to_vec();
                child_path.push(key.to_string());
                find_sub_no_vars(val, &child_path, re, issues);
            }
        }
        AstNode::Array(arr) => {
            for (i, elem) in arr.elements.iter().enumerate() {
                let mut child_path = path.to_vec();
                child_path.push(i.to_string());
                find_sub_no_vars(elem, &child_path, re, issues);
            }
        }
        _ => {}
    }
}

crate::register_cfn_lint_rule!(W1020);
