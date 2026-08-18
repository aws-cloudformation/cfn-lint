use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

static GLOBALS_SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/sam/globals.json"
    ))
    .unwrap_or_default()
});

const TRANSFORM_SAM: &str = "AWS::Serverless-2016-10-31";

pub struct E3722;

impl CfnLintRule for E3722 {
    fn id(&self) -> &str {
        "E3722"
    }
    fn short_description(&self) -> &str {
        "Validate Globals section"
    }
    fn description(&self) -> &str {
        "The Globals section is only valid in SAM templates. \
         Check that the Serverless transform is declared and \
         validate the Globals section structure."
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }
    fn keywords(&self) -> &[&str] {
        &["Globals"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let globals = match root.get("Globals") {
            Some(n) => n,
            None => return vec![],
        };

        // Check SAM transform is present
        let has_sam_transform = root
            .get("Transform")
            .map(|t| {
                if let Some(s) = t.as_str() {
                    s == TRANSFORM_SAM
                } else if let Some(arr) = t.as_array() {
                    arr.elements
                        .iter()
                        .any(|e| e.as_str() == Some(TRANSFORM_SAM))
                } else {
                    false
                }
            })
            .unwrap_or(false);

        if !has_sam_transform {
            return vec![ValidationError {
                rule_id: Some("E3722".to_string()),
                message: format!(
                    "'Globals' section requires the serverless transform {:?}",
                    TRANSFORM_SAM
                ),
                path: vec!["Globals".to_string()],
                span: globals.span(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        // Validate Globals structure against the schema
        let validator = crate::jsonschema::Validator::new(GLOBALS_SCHEMA.clone());
        let path = vec!["Globals".to_string()];
        validator
            .validate(globals, &GLOBALS_SCHEMA, &path)
            .into_iter()
            .map(|err| ValidationError {
                rule_id: Some("E3722".to_string()),
                message: err.message,
                path: err.path,
                span: err.span,
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            })
            .collect()
    }
}

crate::register_cfn_lint_rule!(E3722);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
    use crate::parser;

    #[test]
    fn test_globals_without_sam_transform() {
        let yaml = br#"
Globals:
  Function:
    Timeout: 30
Resources:
  MyFunction:
    Type: AWS::Lambda::Function
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("serverless transform"));
    }

    #[test]
    fn test_globals_with_sam_transform_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_with_sam_transform_in_array() {
        let yaml = br#"
Transform:
  - AWS::Serverless-2016-10-31
  - AWS::LanguageExtensions
Globals:
  Function:
    Timeout: 30
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_api_section_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Api:
    TracingEnabled: true
    CacheClusterEnabled: false
    Name: MyApi
Resources:
  MyApi:
    Type: AWS::Serverless::Api
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_http_api_section_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  HttpApi:
    PropagateTags: true
Resources:
  MyHttpApi:
    Type: AWS::Serverless::HttpApi
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_simple_table_section_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  SimpleTable:
    SSESpecification: {}
Resources:
  MyTable:
    Type: AWS::Serverless::SimpleTable
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_state_machine_section_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  StateMachine:
    PropagateTags: true
Resources:
  MyStateMachine:
    Type: AWS::Serverless::StateMachine
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_layer_version_section_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  LayerVersion:
    PublishLambdaVersion: true
Resources:
  MyLayer:
    Type: AWS::Serverless::LayerVersion
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_capacity_provider_section_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  CapacityProvider:
    PropagateTags: true
    KmsKeyArn: arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012
Resources:
  MyCapacityProvider:
    Type: AWS::Serverless::CapacityProvider
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_websocket_api_section_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  WebSocketApi:
    PropagateTags: true
    DisableExecuteApiEndpoint: false
    RouteSelectionExpression: $request.body.action
Resources:
  MyWebSocketApi:
    Type: AWS::Serverless::WebSocketApi
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_all_sections_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
  Api:
    TracingEnabled: true
  HttpApi:
    PropagateTags: true
  SimpleTable:
    SSESpecification: {}
  StateMachine:
    PropagateTags: true
  LayerVersion:
    PublishLambdaVersion: true
  CapacityProvider:
    PropagateTags: true
  WebSocketApi:
    PropagateTags: true
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "unexpected errors: {:?}", errors);
    }

    #[test]
    fn test_globals_invalid_section() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  InvalidSection:
    SomeProperty: value
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(!errors.is_empty(), "expected error for invalid section");
    }

    #[test]
    fn test_globals_invalid_property_in_function() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    NotAValidProperty: value
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(!errors.is_empty(), "expected error for invalid property");
    }

    #[test]
    fn test_no_globals_section() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let errors = E3722.validate_template(&tmpl, &ast);
        assert!(errors.is_empty(), "no errors expected when Globals absent");
    }
}
