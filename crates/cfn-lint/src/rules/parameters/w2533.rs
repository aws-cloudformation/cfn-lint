use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W2533: Check required properties for Lambda if the deployment package is a .zip file.
///
/// For AWS::Lambda::Function, Zip deployment is indicated by PackageType: Zip or
/// Code with ZipFile/S3Key.
///
/// For AWS::Serverless::Function, Zip deployment is indicated by PackageType: Zip,
/// or inferred from CodeUri/InlineCode (unless ImageUri is present or PackageType is Image).
pub struct W2533;

impl CfnLintRule for W2533 {
    fn id(&self) -> &str {
        "W2533"
    }
    fn short_description(&self) -> &str {
        "Check required properties for Lambda if the deployment package is a .zip file"
    }
    fn description(&self) -> &str {
        "When the package type is Zip, you must also specify the handler and runtime properties"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::Lambda::Function/Properties",
            "Resources/AWS::Serverless::Function/Properties",
        ]
    }

    fn validate(
        &self,
        _validator: &Validator,
        keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let props = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        // Determine if this is a Serverless::Function based on the keyword
        let is_serverless = keyword.contains("AWS::Serverless::Function");

        let is_zip = if is_serverless {
            self.is_serverless_zip_deployment(props)
        } else {
            self.is_lambda_zip_deployment(props)
        };

        if !is_zip {
            return vec![];
        }

        let mut missing = Vec::new();
        if props.get("Handler").is_none() {
            missing.push("Handler");
        }
        if props.get("Runtime").is_none() {
            missing.push("Runtime");
        }

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

impl W2533 {
    /// Check if AWS::Lambda::Function is a Zip deployment.
    fn is_lambda_zip_deployment(&self, props: &crate::ast::ObjectNode) -> bool {
        if props.get("PackageType").and_then(|p| p.as_str()) == Some("Zip") {
            return true;
        }
        if let Some(code) = props.get("Code") {
            if code.get("ZipFile").is_some() || code.get("S3Key").is_some() {
                return true;
            }
        }
        // No Code property - cannot determine deployment type
        false
    }

    /// Check if AWS::Serverless::Function is a Zip deployment.
    ///
    /// SAM functions are Zip by default unless PackageType is "Image".
    /// PackageType is authoritative - check it first before inferring from other properties.
    fn is_serverless_zip_deployment(&self, props: &crate::ast::ObjectNode) -> bool {
        let package_type = props.get("PackageType").and_then(|p| p.as_str());

        // PackageType is authoritative when present
        if package_type == Some("Image") {
            return false;
        }
        if package_type == Some("Zip") {
            return true;
        }

        // PackageType not set - infer from other properties
        // ImageUri implies Image package type
        if props.get("ImageUri").is_some() {
            return false;
        }

        // CodeUri or InlineCode indicates Zip deployment
        if props.get("CodeUri").is_some() || props.get("InlineCode").is_some() {
            return true;
        }

        // Default is Zip package type for SAM functions
        // (no CodeUri/InlineCode/ImageUri means code will be provided at
        // deployment time as zip)
        true
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
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
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
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("Handler"));
    }

    #[test]
    fn test_serverless_zip_with_handler_and_runtime_ok() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello_world/
      Handler: app.handler
      Runtime: python3.12
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_serverless_zip_missing_handler_warns() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello_world/
      Runtime: python3.12
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("Handler"));
    }

    #[test]
    fn test_serverless_zip_missing_both_warns() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello_world/
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("Handler"));
        assert!(errors[0].message.contains("Runtime"));
    }

    #[test]
    fn test_serverless_image_skipped() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Image
      ImageUri: 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        // No errors because PackageType: Image doesn't require Handler/Runtime
        assert!(errors.is_empty());
    }

    #[test]
    fn test_serverless_imageuri_implies_image() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      ImageUri: 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        // ImageUri implies Image package type, so no errors
        assert!(errors.is_empty());
    }

    #[test]
    fn test_serverless_explicit_zip_overrides_imageuri() {
        // If PackageType: Zip is set explicitly, it takes precedence over ImageUri
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      PackageType: Zip
      ImageUri: 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-repo:latest
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        // PackageType: Zip is explicit, so Handler/Runtime are required
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("Handler"));
        assert!(errors[0].message.contains("Runtime"));
    }

    #[test]
    fn test_serverless_inlinecode_is_zip() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      InlineCode: |
        def handler(event, context):
            return 'Hello'
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        // InlineCode indicates Zip, so Handler/Runtime are required
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("Handler"));
        assert!(errors[0].message.contains("Runtime"));
    }

    #[test]
    fn test_serverless_default_is_zip() {
        // SAM function with no CodeUri/InlineCode/ImageUri defaults to Zip
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      Description: A function
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2533.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties",
            instance,
            &serde_json::json!({}),
            &path,
        );
        // Default is Zip, so Handler/Runtime are required
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("Handler"));
        assert!(errors[0].message.contains("Runtime"));
    }
}

crate::register_cfn_lint_rule!(W2533);
