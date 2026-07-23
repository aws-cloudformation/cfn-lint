use std::collections::VecDeque;

use crate::ast::AstNode;
use crate::helpers::get_value_from_path;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3673: Validate if an ImageId is required for an EC2 Instance.
pub struct E3673;

impl CfnLintRule for E3673 {
    fn id(&self) -> &str {
        "E3673"
    }
    fn short_description(&self) -> &str {
        "Validate if an ImageId is required"
    }
    fn description(&self) -> &str {
        "Validate if an ImageId is required. It can be required if the \
         associated LaunchTemplate doesn't specify an ImageId"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::EC2::Instance/Properties"]
    }

    fn validate(
        &self,
        validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let ctx = match validator.context() {
            Some(c) => c.clone(),
            None => return vec![],
        };

        let mut errors = Vec::new();
        for (image_id, image_ctx) in get_value_from_path(
            &ctx,
            Some(instance),
            &mut VecDeque::from(["ImageId".to_string()]),
        ) {
            if image_id.is_some() {
                continue;
            }
            // No ImageId -- check for LaunchTemplate
            let has_lt = get_value_from_path(
                &image_ctx,
                Some(instance),
                &mut VecDeque::from(["LaunchTemplate".to_string()]),
            )
            .iter()
            .any(|(v, _)| v.is_some());

            if !has_lt {
                errors.push(ValidationError {
                    rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message:
                        "'ImageId' is a required property when 'LaunchTemplate' is not provided"
                            .to_string(),
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_validate_is_stub() {
        let yaml = br#"
Resources:
  Instance:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t2.micro
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3673.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3673);
