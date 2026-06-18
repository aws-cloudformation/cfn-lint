use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W3700;

impl CfnLintRule for W3700 {
    fn id(&self) -> &str {
        "W3700"
    }
    fn short_description(&self) -> &str {
        "Non-standard Domain values are converted to vpc"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::EC2::EIP/Properties/Domain"]
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

        let lower = value.to_lowercase();
        if lower != "standard" && lower != "vpc" {
            return vec![ValidationError {
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "'{}' is not a standard Domain value. Non-standard values are silently converted to 'vpc'.",
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

crate::register_cfn_lint_rule!(W3700);
