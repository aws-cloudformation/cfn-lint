use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use regex::Regex;
use std::sync::LazyLock;

static RE_SUB_VARS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\$\{([^}]+)\}").unwrap()
});

pub struct W1019;

impl CfnLintRule for W1019 {
    fn id(&self) -> &str { "W1019" }
    fn short_description(&self) -> &str { "Validate that parameters to a Fn::Sub are used" }
    fn severity(&self) -> Severity { Severity::Warning }

    fn keywords(&self) -> &[&str] {
        &["Fn/Sub"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let func = match instance.as_function() {
            Some(f) if f.name == "Fn::Sub" => f,
            _ => return vec![],
        };

        let arr = match func.args.as_array() {
            Some(a) if a.elements.len() == 2 => a,
            _ => return vec![],
        };

        let template_str = match arr.elements[0].as_str() {
            Some(s) => s,
            None => return vec![],
        };

        let context_map = match arr.elements[1].as_object() {
            Some(o) => o,
            None => return vec![],
        };

        let used_vars: Vec<&str> = RE_SUB_VARS.captures_iter(template_str)
            .filter_map(|c| c.get(1).map(|m| m.as_str()))
            .collect();

        let mut issues = Vec::new();
        for (key, value) in context_map.iter() {
            if !used_vars.contains(&key) {
                issues.push(ValidationError {
                    keyword: format!("cfnLint:{}", self.id()),
                    message: format!("Parameter '{}' not used in 'Fn::Sub'", key),
                    path: path.to_vec(),
                    span: value.span(),
                    ..Default::default()
                });
            }
        }
        issues
    }
}

crate::register_cfn_lint_rule!(W1019);
