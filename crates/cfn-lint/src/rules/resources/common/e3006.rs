use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E3006;

impl CfnLintRule for E3006 {
    fn id(&self) -> &str { "E3006" }
    fn short_description(&self) -> &str { "Validate the CloudFormation resource type" }
    fn description(&self) -> &str { "Validates resource types are valid CloudFormation types" }
    fn severity(&self) -> Severity { Severity::Error }
    fn keywords(&self) -> &[&str] { &["Resources/*"] }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        if !schema.is_null() {
            return vec![];
        }

        let resource_type = match instance.get("Type").and_then(|t| t.as_str()) {
            Some(t) => t,
            None => return vec![],
        };

        if resource_type.starts_with("Custom::")
            || resource_type.ends_with("::MODULE")
            || resource_type.starts_with("AWS::Serverless::")
            || resource_type == "AWS::CDK::Metadata"
        {
            return vec![];
        }

        let region = validator.context()
            .and_then(|ctx| ctx.regions.first().cloned())
            .unwrap_or_else(|| "us-east-1".to_string());

        let span = instance.get("Type").map(|n| n.span()).unwrap_or_default();
        let mut type_path = path.to_vec();
        type_path.push("Type".to_string());

        vec![ValidationError::new(
            self.id(),
            format!("Resource type '{}' does not exist in '{}'", resource_type, region),
            type_path,
            span,
        )]
    }
}

crate::register_cfn_lint_rule!(E3006);
