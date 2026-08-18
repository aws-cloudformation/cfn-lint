use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;

/// W3001: SAM resource-level properties are ignored.
///
/// Unknown resource-level properties (siblings of Type/Properties) on
/// AWS::Serverless::* resources are silently ignored by the SAM transform.
/// The template still deploys, but the value is lost.
///
/// This is a child rule of E3001 — when E3001 detects an unknown resource-level
/// key on a SAM resource, it reports W3001 (warning) instead of E3001 (error).
///
/// Source: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification.html
pub struct W3001;

impl CfnLintRule for W3001 {
    fn id(&self) -> &str {
        "W3001"
    }

    fn short_description(&self) -> &str {
        "SAM resource-level properties are ignored"
    }

    fn description(&self) -> &str {
        "Unknown resource-level properties on AWS::Serverless resources are ignored \
         by the SAM transform. Move supported resource properties under Properties."
    }

    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        // W3001 is dispatched from E3001, not via keywords
        &[]
    }
}

crate::register_cfn_lint_rule!(W3001);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::rules::resources::common::e3001::E3001;
    use crate::template::Template;

    #[test]
    fn test_serverless_function_with_unknown_attr_warns_w3001() {
        let yaml = br#"
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Description: This should trigger W3001 not E3001
    Properties:
      Runtime: python3.9
      Handler: index.handler
      CodeUri: ./src
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();

        let errors = E3001.validate_template(&tmpl, &ast);

        // Should have exactly one error for the Description key
        assert_eq!(errors.len(), 1, "Expected 1 error, got {:?}", errors);
        let err = &errors[0];

        // Should be W3001, not E3001
        assert_eq!(
            err.rule_id.as_deref(),
            Some("W3001"),
            "Expected W3001 for SAM resource, got {:?}",
            err.rule_id
        );

        // Message should indicate it's ignored by SAM transform
        assert!(
            err.message.contains("ignored by the SAM transform"),
            "Expected message about SAM transform, got: {}",
            err.message
        );

        // Path points to the resource (the unknown key is mentioned in the message)
        assert_eq!(
            err.path,
            vec!["Resources", "MyFunction"],
            "Expected path to resource, got {:?}",
            err.path
        );
    }

    #[test]
    fn test_s3_bucket_with_unknown_attr_errors_e3001() {
        let yaml = br#"
AWSTemplateFormatVersion: "2010-09-09"
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Description: This should trigger E3001 error
    Properties:
      BucketName: my-bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();

        let errors = E3001.validate_template(&tmpl, &ast);

        // Should have exactly one error for the Description key
        assert_eq!(errors.len(), 1, "Expected 1 error, got {:?}", errors);
        let err = &errors[0];

        // Should be E3001, NOT W3001
        assert_eq!(
            err.rule_id.as_deref(),
            Some("E3001"),
            "Expected E3001 for non-SAM resource, got {:?}",
            err.rule_id
        );

        // Message should be the standard additionalProperties message
        assert!(
            err.message
                .contains("Additional properties are not allowed")
                || err.message.contains("does not match"),
            "Expected standard additionalProperties message, got: {}",
            err.message
        );

        // Path points to the resource (the unknown key is mentioned in the message)
        assert_eq!(
            err.path,
            vec!["Resources", "MyBucket"],
            "Expected path to resource, got {:?}",
            err.path
        );
    }

    #[test]
    fn test_serverless_api_with_unknown_attr_warns_w3001() {
        let yaml = br#"
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyApi:
    Type: AWS::Serverless::Api
    Foo: bar
    Properties:
      StageName: prod
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();

        let errors = E3001.validate_template(&tmpl, &ast);

        // Should have exactly one error for the Foo key
        assert_eq!(errors.len(), 1, "Expected 1 error, got {:?}", errors);
        let err = &errors[0];

        // Should be W3001
        assert_eq!(
            err.rule_id.as_deref(),
            Some("W3001"),
            "Expected W3001 for SAM resource, got {:?}",
            err.rule_id
        );
    }

    #[test]
    fn test_serverless_function_valid_attrs_no_errors() {
        let yaml = br#"
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Condition: IsProduction
    DependsOn: MyBucket
    Metadata:
      BuildMethod: makefile
    Properties:
      Runtime: python3.9
      Handler: index.handler
      CodeUri: ./src
  MyBucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();

        let errors = E3001.validate_template(&tmpl, &ast);

        // No errors - all attributes are valid
        assert!(
            errors.is_empty(),
            "Expected no errors for valid attributes, got {:?}",
            errors
        );
    }

    #[test]
    fn test_lambda_function_with_unknown_attr_errors_e3001() {
        // AWS::Lambda::Function is NOT a SAM type, should get E3001
        let yaml = br#"
AWSTemplateFormatVersion: "2010-09-09"
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
    Description: This is NOT a SAM resource
    Properties:
      Runtime: python3.9
      Handler: index.handler
      Code:
        ZipFile: |
          def handler(event, context):
            return "Hello"
      Role: arn:aws:iam::123456789012:role/lambda-role
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();

        let errors = E3001.validate_template(&tmpl, &ast);

        // Should have exactly one error for the Description key
        assert_eq!(errors.len(), 1, "Expected 1 error, got {:?}", errors);
        let err = &errors[0];

        // Should be E3001, NOT W3001
        assert_eq!(
            err.rule_id.as_deref(),
            Some("E3001"),
            "Expected E3001 for AWS::Lambda::Function, got {:?}",
            err.rule_id
        );
    }
}
