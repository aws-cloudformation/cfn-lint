use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W2533: Check required properties for Lambda if the deployment package is a .zip file.
pub struct W2533;

impl CfnLintRule for W2533 {
    fn id(&self) -> &str { "W2533" }
    fn short_description(&self) -> &str {
        "Check required properties for Lambda if the deployment package is a .zip file"
    }
    fn description(&self) -> &str {
        "When the package type is Zip, you must also specify the handler and runtime properties"
    }
    fn severity(&self) -> Severity { Severity::Warning }

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

        let is_zip = if props.get("PackageType").and_then(|p| p.as_str()) == Some("Zip") {
            true
        } else if let Some(code) = props.get("Code") {
            code.get("ZipFile").is_some() || code.get("S3Key").is_some()
        } else {
            // No Code property - cannot determine deployment type, skip
            false
        };

        if !is_zip {
            return vec![];
        }

        let mut missing = Vec::new();
        if props.get("Handler").is_none() { missing.push("Handler"); }
        if props.get("Runtime").is_none() { missing.push("Runtime"); }

        if !missing.is_empty() {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "Properties {:?} missing for zip file deployment at {}",
                    missing,
                    path.join("/"),
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

    #[test]
    fn test_zip_with_handler_and_runtime_ok() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      PackageType: Zip
      Handler: index.handler
      Runtime: python3.12
      Code:
        S3Bucket: my-bucket
        S3Key: code.zip
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Func").unwrap()
            .get("Properties").unwrap();
        let path = vec![
            "Resources".to_string(), "Func".to_string(), "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(&validator, "Resources/AWS::Lambda::Function/Properties", instance, &serde_json::json!({}), &path);
        assert!(errors.is_empty());
    }

    #[test]
    fn test_zip_missing_handler_warns() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      PackageType: Zip
      Runtime: python3.12
      Code:
        S3Bucket: my-bucket
        S3Key: code.zip
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Func").unwrap()
            .get("Properties").unwrap();
        let path = vec![
            "Resources".to_string(), "Func".to_string(), "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(&validator, "Resources/AWS::Lambda::Function/Properties", instance, &serde_json::json!({}), &path);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("Handler"));
    }
}

crate::register_cfn_lint_rule!(W2533);
