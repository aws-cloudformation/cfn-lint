use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;
use regex::Regex;
use std::sync::LazyLock;

static RE_DYN_REF_SPACES: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\{\{\s+resolve:|\{\{resolve\s+:").unwrap());

pub struct W1053;

impl CfnLintRule for W1053 {
    fn id(&self) -> &str {
        "W1053"
    }
    fn short_description(&self) -> &str {
        "Dynamic references should not contain spaces"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<ValidationError> {
        let mut issues = Vec::new();
        crate::ast::walk(root, &[], &mut |node, path| {
            if let Some(s) = node.as_str() {
                if RE_DYN_REF_SPACES.is_match(s) {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!(
                            "'{}' has spaces and will not be resolved as a dynamic reference. Remove spaces from '{{{{resolve:...}}}}'",
                            s
                        ),
                        path: path.to_vec(),
                        span: node.span(),
                        ..Default::default()
                    });
                }
            }
            true
        });
        issues
    }
}

crate::register_cfn_lint_rule!(W1053);
