use crate::ast::{AstNode, Span};
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use crate::template::Template;

/// E3058: Validate at least one of the properties are required.
pub struct E3058;

impl CfnLintRule for E3058 {
    fn id(&self) -> &str {
        "E3058"
    }
    fn short_description(&self) -> &str {
        "At least one of the required properties must exist"
    }
    fn description(&self) -> &str {
        "Validates that at least one of the listed properties is present"
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

        let req_or = match schema.get("requiredOr").and_then(|r| r.as_array()) {
            Some(a) => a,
            None => return vec![],
        };

        let names: Vec<&str> = req_or.iter().filter_map(|v| v.as_str()).collect();
        if names.is_empty() {
            return vec![];
        }

        let mut props_path = path.to_vec();
        props_path.push("Properties".to_string());

        vec![ValidationError::new(
            self.id(),
            format!("One of {:?} is a required property", names),
            props_path,
            Span::default(),
        )]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(E3058);
