use crate::ast::{AstNode, Span};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use crate::template::Template;

/// E3003: Required Resource properties are missing.
pub struct E3003;

impl CfnLintRule for E3003 {
    fn id(&self) -> &str {
        "E3003"
    }
    fn short_description(&self) -> &str {
        "Required Resource properties are missing"
    }
    fn description(&self) -> &str {
        "Make sure that Resources properties that are required exist"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }
    fn keywords(&self) -> &[&str] {
        &["Resources/*"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        if schema.is_null() {
            return vec![];
        }
        if instance.get("Properties").is_some() {
            return vec![];
        }

        let mut issues = Vec::new();
        if let Some(req) = schema.get("required").and_then(|r| r.as_array()) {
            for r in req {
                if let Some(n) = r.as_str() {
                    let mut props_path = path.to_vec();
                    props_path.push("Properties".to_string());
                    issues.push(ValidationError::new(
                        self.id(),
                        format!("Property \"{}\" is required", n),
                        props_path,
                        Span::default(),
                    ));
                }
            }
        }
        issues
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(E3003);
