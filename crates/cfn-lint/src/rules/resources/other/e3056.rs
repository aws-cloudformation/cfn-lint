use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3056: EC2 health check type cannot be combined with other types
pub struct E3056;

impl CfnLintRule for E3056 {
    fn id(&self) -> &str {
        "E3056"
    }
    fn short_description(&self) -> &str {
        "EC2 health check type cannot be combined with other types"
    }
    fn description(&self) -> &str {
        "When specifying multiple health check types for an Auto Scaling group, \
         EC2 cannot be combined with other health check types."
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::AutoScaling::AutoScalingGroup/Properties/HealthCheckType"]
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

        if !val.contains(',') {
            return vec![];
        }

        let parts: Vec<&str> = val.split(',').map(|s| s.trim()).collect();
        if parts.contains(&"EC2") && parts.len() > 1 {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "EC2 cannot be combined with other health check types. Got {:?}",
                    val
                ),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

#[cfg(test)]

mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_stubbed_out() {
        let yaml = br#"
Resources:
  ASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      HealthCheckType: "EC2, ELB"
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3056.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3056);
