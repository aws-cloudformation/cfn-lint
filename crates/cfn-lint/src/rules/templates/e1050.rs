use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use crate::template::Template;
use regex::Regex;
use std::sync::LazyLock;

static RE_DYN_REF: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"\{\{resolve:([^}]+)\}\}").unwrap()
});

const VALID_SERVICES: &[&str] = &["ssm", "ssm-secure", "secretsmanager"];

pub struct E1050;

impl CfnLintRule for E1050 {
    fn id(&self) -> &str { "E1050" }
    fn short_description(&self) -> &str { "Validate the structure of a dynamic reference" }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] { &["/"] }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<ValidationError> {
        let mut issues = Vec::new();
        crate::ast::walk(root, &[], &mut |node, path| {
            if let Some(s) = node.as_str() {
                for cap in RE_DYN_REF.captures_iter(s) {
                    let inner = &cap[1];
                    let parts: Vec<&str> = inner.split(':').collect();
                    if parts.len() < 2 {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!("Dynamic reference '{{{{resolve:{}}}}}' is missing service type", inner),
                            path: path.to_vec(),
                            span: node.span(),
                            ..Default::default()
                        });
                        continue;
                    }
                    let service = parts[0];
                    if !VALID_SERVICES.contains(&service) {
                        issues.push(ValidationError {
                            rule_id: Some(self.id().to_string()),
                            message: format!("'{}' is not one of {:?}", service, VALID_SERVICES),
                            path: path.to_vec(),
                            span: node.span(),
                            ..Default::default()
                        });
                    }
                }
            }
            true
        });
        issues
    }
}

crate::register_cfn_lint_rule!(E1050);
