use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W2511;

impl CfnLintRule for W2511 {
    fn id(&self) -> &str {
        "W2511"
    }
    fn short_description(&self) -> &str {
        "Check IAM Resource Policies syntax"
    }
    fn description(&self) -> &str {
        "IAM Policy Version should be updated to 2012-10-17"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/*/Properties/PolicyDocument/Version",
            "Resources/*/Properties/Policies/*/PolicyDocument/Version",
            "Resources/*/Properties/AssumeRolePolicyDocument/Version",
            "Resources/*/Properties/KeyPolicy/Version",
            "Resources/*/Properties/AccessPolicies/Version",
            "Resources/*/Properties/InlinePolicy/Version",
        ]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let val = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };
        if val == "2008-10-17" {
            vec![ValidationError {
                rule_id: None,
                message: "IAM Policy Version should be updated to '2012-10-17'".to_string(),
                path: path.to_vec(),
                keyword: String::new(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }]
        } else {
            vec![]
        }
    }
}

crate::register_cfn_lint_rule!(W2511);
