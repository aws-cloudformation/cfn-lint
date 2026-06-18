use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3716: Validate Lambda layer ARN length based on region
pub struct E3716;

impl CfnLintRule for E3716 {
    fn id(&self) -> &str { "E3716" }
    fn short_description(&self) -> &str {
        "Validate Lambda layer ARN length based on region"
    }
    fn description(&self) -> &str {
        "Validates the Lambda layer ARN length based on region. \
         Max length is 176 + len(partition) + len(region)."
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Lambda::Function/Properties/Layers/*"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let val = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        let regions = match validator.context() {
            Some(ctx) => ctx.regions.clone(),
            None => vec!["us-east-1".to_string()],
        };

        let mut errors = Vec::new();
        for region in &regions {
            let partition = get_partition(region);
            let max_length = 176 + partition.len() + region.len();
            if val.len() > max_length {
                errors.push(ValidationError {
                rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: format!(
                        "{:?} is longer than {} in {:?}",
                        val, max_length, region
                    ),
                    path: path.to_vec(),
                    span: instance.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
            }
        }

        errors
    }
}

fn get_partition(region: &str) -> &'static str {
    if region.starts_with("cn-") {
        "aws-cn"
    } else if region.starts_with("us-gov-") {
        "aws-us-gov"
    } else if region.starts_with("us-iso-") || region.starts_with("us-isof-") {
        "aws-iso"
    } else if region.starts_with("us-isob-") {
        "aws-iso-b"
    } else if region.starts_with("eu-isoe-") {
        "aws-iso-e"
    } else if region.starts_with("eusc-") {
        "aws-iso-f"
    } else {
        "aws"
    }
}

#[cfg(test)]

mod tests {
    use crate::template::Template;
    use super::*;
    use crate::parser;

    #[test]
    fn test_stubbed_out() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Layers:
        - arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3716.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3716);
