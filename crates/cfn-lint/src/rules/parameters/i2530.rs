use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// I2530: Validate that SnapStart is configured for >= Java11 runtimes.
///
/// SnapStart is a no-cost feature that can increase performance up to 10x.
/// Enable SnapStart for Java 11 and greater runtimes.
pub struct I2530;

impl CfnLintRule for I2530 {
    fn id(&self) -> &str {
        "I2530"
    }
    fn short_description(&self) -> &str {
        "Validate that SnapStart is configured for >= Java11 runtimes"
    }
    fn description(&self) -> &str {
        "SnapStart is a no-cost feature that can increase performance up to 10x. \
         Enable SnapStart for Java 11 and greater runtimes"
    }
    fn severity(&self) -> Severity {
        Severity::Informational
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Lambda::Function/Properties"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let props = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        let runtime = match props.get("Runtime").and_then(|n| n.as_str()) {
            Some(r) => r,
            None => return vec![],
        };

        if !runtime.starts_with("java") || runtime == "java8.al2" || runtime == "java8" {
            return vec![];
        }

        // Check if SnapStart is already configured
        let has_snapstart = props
            .get("SnapStart")
            .and_then(|s| s.as_object())
            .and_then(|s| s.get("ApplyOn"))
            .and_then(|a| a.as_str())
            .map(|v| v != "None")
            .unwrap_or(false);

        if !has_snapstart {
            let mut err_path = path.to_vec();
            err_path.push("SnapStart".to_string());
            err_path.push("ApplyOn".to_string());

            let span = props.get("Runtime")
                .map(|n| n.span())
                .unwrap_or_default();

            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "'{}' runtime should consider using 'SnapStart'",
                    runtime
                ),
                path: err_path,
                span,
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

    #[test]
    fn test_java11_without_snapstart() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: java11
      Handler: com.example.Handler
      Code:
        S3Bucket: my-bucket
        S3Key: code.zip
      Role: arn:aws:iam::123456789012:role/role
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Func").unwrap()
            .get("Properties").unwrap();
        let path = vec![
            "Resources".to_string(), "Func".to_string(), "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I2530.validate(&validator, "Resources/AWS::Lambda::Function/Properties", instance, &serde_json::json!({}), &path);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("SnapStart"));
    }

    #[test]
    fn test_java8_no_issue() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: java8
      Handler: com.example.Handler
      Code:
        S3Bucket: my-bucket
        S3Key: code.zip
      Role: arn:aws:iam::123456789012:role/role
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Func").unwrap()
            .get("Properties").unwrap();
        let path = vec![
            "Resources".to_string(), "Func".to_string(), "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = I2530.validate(&validator, "Resources/AWS::Lambda::Function/Properties", instance, &serde_json::json!({}), &path);
        assert!(errors.is_empty());
    }
}

crate::register_cfn_lint_rule!(I2530);
