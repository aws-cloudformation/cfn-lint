use crate::ast::AstNode;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use crate::template::Template;
use crate::transform::is_sam_template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

pub struct W3002;

impl CfnLintRule for W3002 {
    fn id(&self) -> &str {
        "W3002"
    }

    fn short_description(&self) -> &str {
        "Warn when properties are configured to only work with the package command"
    }

    fn description(&self) -> &str {
        "Some properties can be configured to only work with the CloudFormation package command"
    }

    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::ApiGateway::RestApi/Properties/BodyS3Location",
            "Resources/AWS::Lambda::Function/Properties/Code",
            "Resources/AWS::Lambda::LayerVersion/Properties/Content",
            "Resources/AWS::ElasticBeanstalk::ApplicationVersion/Properties/SourceBundle",
            "Resources/AWS::StepFunctions::StateMachine/Properties/DefinitionS3Location",
            "Resources/AWS::AppSync::GraphQLSchema/Properties/DefinitionS3Location",
            "Resources/AWS::AppSync::Resolver/Properties/RequestMappingTemplateS3Location",
            "Resources/AWS::AppSync::Resolver/Properties/ResponseMappingTemplateS3Location",
            "Resources/AWS::AppSync::FunctionConfiguration/Properties/RequestMappingTemplateS3Location",
            "Resources/AWS::AppSync::FunctionConfiguration/Properties/ResponseMappingTemplateS3Location",
            "Resources/AWS::CloudFormation::Stack/Properties/TemplateURL",
            "Resources/AWS::CodeCommit::Repository/Properties/Code/S3",
        ]
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

        // Skip if inside a function context
        let functions = [
            "Fn::If", "Fn::Select", "Fn::GetAtt", "Fn::Sub", "Fn::Join",
            "Fn::Split", "Fn::FindInMap", "Ref",
        ];
        if path.iter().any(|p| functions.contains(&p.as_str())) {
            return vec![];
        }

        // Skip if SAM template
        if let Some(ctx) = validator.context() {
            if is_sam_template(&ctx.template.root) {
                return vec![];
            }
        }

        // S3 URIs and HTTPS URLs are fine
        if val.starts_with("s3://") || val.starts_with("https://") {
            return vec![];
        }

        // Dynamic references are fine
        if val.contains("{{resolve:") {
            return vec![];
        }

        vec![ValidationError {
                rule_id: None,
            keyword: format!("cfnLint:{}", CfnLintRule::id(self)),
            message: "This code may only work with 'package' cli command".to_string(),
            path: path.to_vec(),
            span: instance.span(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        }]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        vec![]
    }
}

crate::register_cfn_lint_rule!(W3002);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_no_issues_for_s3_uri() {
        let yaml = br#"
Resources:
  Stack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: s3://bucket/template.yaml
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3002.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_local_path_stub() {
        let yaml = br#"
Resources:
  Stack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: ./nested.yaml
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3002.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_skip_sam_template() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  Stack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: ./nested.yaml
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3002.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_stub() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(W3002.validate_template(&tmpl, &ast).is_empty());
    }
}
