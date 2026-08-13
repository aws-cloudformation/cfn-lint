use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W2530: Validate that SnapStart is properly configured with a Lambda Version resource
/// (for AWS::Lambda::Function) or AutoPublishAlias (for AWS::Serverless::Function).
pub struct W2530;

impl CfnLintRule for W2530 {
    fn id(&self) -> &str {
        "W2530"
    }
    fn short_description(&self) -> &str {
        "Validate that SnapStart is properly configured"
    }
    fn description(&self) -> &str {
        "To properly leverage SnapStart, you must configure both the lambda function \
         and attach a Lambda version resource (for AWS::Lambda::Function) or configure \
         AutoPublishAlias (for AWS::Serverless::Function)"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::Lambda::Function/Properties/SnapStart/ApplyOn",
            "Resources/AWS::Serverless::Function/Properties/SnapStart/ApplyOn",
        ]
    }

    fn validate(
        &self,
        validator: &Validator,
        keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let val = match instance.as_str() {
            Some(v) => v,
            None => return vec![],
        };

        if val != "PublishedVersions" {
            return vec![];
        }

        // Get the resource name from the path: Resources/<name>/Properties/SnapStart/ApplyOn
        let resource_name = match path.get(1) {
            Some(n) => n,
            None => return vec![],
        };

        // Determine if this is a Serverless::Function based on the keyword
        let is_serverless = keyword.contains("AWS::Serverless::Function");

        if is_serverless {
            // For AWS::Serverless::Function, check for AutoPublishAlias
            return self.validate_serverless_snapstart(validator, resource_name, instance, path);
        }

        // For AWS::Lambda::Function, check for attached AWS::Lambda::Version
        self.validate_lambda_snapstart(validator, resource_name, instance, path)
    }
}

impl W2530 {
    fn validate_serverless_snapstart(
        &self,
        validator: &Validator,
        resource_name: &str,
        instance: &AstNode,
        path: &[String],
    ) -> Vec<ValidationError> {
        let ctx = match validator.context() {
            Some(c) => c,
            None => return vec![],
        };

        let resource = match ctx.template.resources.get(resource_name) {
            Some(r) => r,
            None => return vec![],
        };

        let props = match &resource.properties {
            Some(p) => p,
            None => {
                // No Properties, so no AutoPublishAlias
                return vec![ValidationError {
                    rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: "'SnapStart' is enabled but 'AutoPublishAlias' is not configured"
                        .into(),
                    path: path.to_vec(),
                    span: instance.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }];
            }
        };

        // Check if AutoPublishAlias is set (any non-null value)
        if props.get("AutoPublishAlias").is_some() {
            return vec![];
        }

        vec![ValidationError {
            rule_id: None,
            keyword: format!("cfnLint:{}", self.id()),
            message: "'SnapStart' is enabled but 'AutoPublishAlias' is not configured".into(),
            path: path.to_vec(),
            span: instance.span(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        }]
    }

    fn validate_lambda_snapstart(
        &self,
        validator: &Validator,
        resource_name: &str,
        instance: &AstNode,
        path: &[String],
    ) -> Vec<ValidationError> {
        // Check if any AWS::Lambda::Version references this function
        let has_version = if let Some(ctx) = validator.context() {
            ctx.template.resources.values().any(|r| {
                if r.resource_type != "AWS::Lambda::Version" {
                    return false;
                }
                if let Some(props) = &r.properties {
                    if let Some(AstNode::Function(f)) = props.get("FunctionName") {
                        if f.name == "Ref" {
                            return f.args.as_str() == Some(resource_name);
                        }
                    }
                }
                false
            })
        } else {
            // Without context, cannot check cross-resource references
            return vec![];
        };

        if !has_version {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: "'SnapStart' is enabled but an 'AWS::Lambda::Version' \
                          resource is not attached"
                    .into(),
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
    fn test_snapstart_with_version_ok() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: java11
      Handler: index.handler
      SnapStart:
        ApplyOn: PublishedVersions
  FuncVersion:
    Type: AWS::Lambda::Version
    Properties:
      FunctionName: !Ref Func
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("SnapStart")
            .unwrap()
            .get("ApplyOn")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "SnapStart".to_string(),
            "ApplyOn".to_string(),
        ];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(
            serde_json::json!({}),
            std::sync::Arc::new(ctx),
        );
        let errors = W2530.validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties/SnapStart/ApplyOn",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_snapstart_without_version_warns() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: java11
      Handler: index.handler
      SnapStart:
        ApplyOn: PublishedVersions
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("SnapStart")
            .unwrap()
            .get("ApplyOn")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "SnapStart".to_string(),
            "ApplyOn".to_string(),
        ];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(
            serde_json::json!({}),
            std::sync::Arc::new(ctx),
        );
        let errors = W2530.validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties/SnapStart/ApplyOn",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("SnapStart"));
        assert!(errors[0].message.contains("AWS::Lambda::Version"));
    }

    #[test]
    fn test_sam_snapstart_with_autopublishalias_ok() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: java11
      Handler: index.handler
      CodeUri: s3://bucket/code.zip
      SnapStart:
        ApplyOn: PublishedVersions
      AutoPublishAlias: live
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("SnapStart")
            .unwrap()
            .get("ApplyOn")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "SnapStart".to_string(),
            "ApplyOn".to_string(),
        ];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(
            serde_json::json!({}),
            std::sync::Arc::new(ctx),
        );
        let errors = W2530.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties/SnapStart/ApplyOn",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_sam_snapstart_without_autopublishalias_warns() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: java11
      Handler: index.handler
      CodeUri: s3://bucket/code.zip
      SnapStart:
        ApplyOn: PublishedVersions
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("SnapStart")
            .unwrap()
            .get("ApplyOn")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "SnapStart".to_string(),
            "ApplyOn".to_string(),
        ];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(
            serde_json::json!({}),
            std::sync::Arc::new(ctx),
        );
        let errors = W2530.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties/SnapStart/ApplyOn",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("SnapStart"));
        assert!(errors[0].message.contains("AutoPublishAlias"));
    }

    #[test]
    fn test_sam_snapstart_with_intrinsic_autopublishalias_ok() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Parameters:
  AliasName:
    Type: String
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: java11
      Handler: index.handler
      CodeUri: s3://bucket/code.zip
      SnapStart:
        ApplyOn: PublishedVersions
      AutoPublishAlias: !Ref AliasName
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("SnapStart")
            .unwrap()
            .get("ApplyOn")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "SnapStart".to_string(),
            "ApplyOn".to_string(),
        ];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(
            serde_json::json!({}),
            std::sync::Arc::new(ctx),
        );
        let errors = W2530.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties/SnapStart/ApplyOn",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_sam_snapstart_applyon_none_ok() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Func:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: java11
      Handler: index.handler
      CodeUri: s3://bucket/code.zip
      SnapStart:
        ApplyOn: None
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("SnapStart")
            .unwrap()
            .get("ApplyOn")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "SnapStart".to_string(),
            "ApplyOn".to_string(),
        ];
        let ctx = crate::context::Context::new(std::sync::Arc::new(tmpl));
        let validator = crate::jsonschema::Validator::new_with_context(
            serde_json::json!({}),
            std::sync::Arc::new(ctx),
        );
        let errors = W2530.validate(
            &validator,
            "Resources/AWS::Serverless::Function/Properties/SnapStart/ApplyOn",
            instance,
            &serde_json::json!({}),
            &path,
        );
        // ApplyOn = None means SnapStart is not enabled, so no warning
        assert!(errors.is_empty());
    }
}

crate::register_cfn_lint_rule!(W2530);
