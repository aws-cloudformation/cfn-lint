use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use fancy_regex::Regex;
use std::sync::LazyLock;

static RE_VALID_NAME: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"^(?i)((?!aws|ssm)[\w.\-]+|/(?!aws|ssm)[\w.\-]+(/[\w.\-]+)*)$").unwrap()
});

pub struct W3701;

impl CfnLintRule for W3701 {
    fn id(&self) -> &str { "W3701" }
    fn short_description(&self) -> &str { "SSM Parameter Name should not use /aws/ or /ssm/ prefix" }
    fn severity(&self) -> Severity { Severity::Warning }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::SSM::Parameter/Properties/Name"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let value = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        if !RE_VALID_NAME.is_match(value).unwrap_or(false) {
            return vec![ValidationError {
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "'{}' does not match the recommended pattern. Parameter names beginning with 'aws' or 'ssm' are reserved.",
                    value
                ),
                path: path.to_vec(),
                span: instance.span(),
                ..Default::default()
            }];
        }

        vec![]
    }
}

crate::register_cfn_lint_rule!(W3701);
