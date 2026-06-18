use regex::Regex;
use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3013: CloudFront Aliases should contain valid domain names.
///
/// Validates that CloudFront distribution aliases are valid domain names:
/// - No double-wildcard patterns like `*.*.example.com`
/// - Must match valid domain name pattern
pub struct E3013;

static DYN_REF_RE: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\{\{resolve:.+\}\}").unwrap());

static DOMAIN_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^(?:[a-z0-9\*](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$")
        .unwrap()
});

impl CfnLintRule for E3013 {
    fn id(&self) -> &str { "E3013" }
    fn short_description(&self) -> &str { "CloudFront Aliases" }
    fn description(&self) -> &str {
        "CloudFront aliases should contain valid domain names"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig/Aliases/*"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let alias = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        // Skip dynamic references
        if DYN_REF_RE.is_match(alias) {
            return vec![];
        }

        let mut errors = Vec::new();

        // Check for invalid wildcard patterns (wildcard not at start, e.g. email.*.example.com)
        if alias.contains(".*.") {
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} contains an invalid wildcard pattern",
                    alias
                ),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }

        // Check valid domain name pattern
        if !DOMAIN_RE.is_match(alias) {
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!("{:?} is not a valid domain name", alias),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }

        errors
    }
}

crate::register_cfn_lint_rule!(E3013);
