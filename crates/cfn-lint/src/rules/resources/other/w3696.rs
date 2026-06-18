use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct W3696;

impl CfnLintRule for W3696 {
    fn id(&self) -> &str {
        "W3696"
    }
    fn short_description(&self) -> &str {
        "Resource type is from a service that is sunsetting"
    }
    fn description(&self) -> &str {
        "Checks if a resource type belongs to an AWS service that is in the sunset phase"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
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
        let is_sunset = schema
            .get("lifecycle")
            .and_then(|l| l.get("status"))
            .and_then(|s| s.as_str())
            == Some("sunset");

        if !is_sunset {
            return vec![];
        }

        let resource_type = match instance.get("Type").and_then(|t| t.as_str()) {
            Some(t) => t,
            None => return vec![],
        };

        let span = instance.get("Type").map(|n| n.span()).unwrap_or_default();
        let mut type_path = path.to_vec();
        type_path.push("Type".to_string());

        vec![ValidationError::new(
            self.id(),
            format!(
                "Resource type '{}' is from a service that is sunsetting",
                resource_type
            ),
            type_path,
            span,
        )]
    }
}

crate::register_cfn_lint_rule!(W3696);
