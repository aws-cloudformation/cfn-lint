use std::collections::HashSet;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use crate::transform::{is_sam_template, is_serverless_type};

const TRANSFORM_SAM: &str = "AWS::Serverless-2016-10-31";

/// Globals section key → resource type mapping.
/// This maps AWS::Serverless::* resource types to their corresponding Globals section key.
static RESOURCE_TYPE_TO_GLOBALS_KEY: &[(&str, &str)] = &[
    ("AWS::Serverless::Function", "Function"),
    ("AWS::Serverless::Api", "Api"),
    ("AWS::Serverless::HttpApi", "HttpApi"),
    ("AWS::Serverless::SimpleTable", "SimpleTable"),
    ("AWS::Serverless::StateMachine", "StateMachine"),
    ("AWS::Serverless::LayerVersion", "LayerVersion"),
    ("AWS::Serverless::CapacityProvider", "CapacityProvider"),
    ("AWS::Serverless::WebSocketApi", "WebSocketApi"),
];

/// Get the Globals section key for a given resource type.
fn globals_key_for_resource_type(resource_type: &str) -> Option<&'static str> {
    RESOURCE_TYPE_TO_GLOBALS_KEY
        .iter()
        .find(|(rt, _)| *rt == resource_type)
        .map(|(_, key)| *key)
}

/// E3066: SAM resource attributes require the Serverless Transform.
///
/// Validates that:
/// - `Connectors` and `IgnoreGlobals` are only used on AWS::Serverless::* resources
/// - The Serverless Transform is declared when these attributes are present
/// - `IgnoreGlobals` must be the string "*" or an array of strings
/// - When `IgnoreGlobals` is an array, each key must be a valid property name
///   defined in the corresponding Globals section for that resource type
pub struct E3066;

impl CfnLintRule for E3066 {
    fn id(&self) -> &str {
        "E3066"
    }
    fn short_description(&self) -> &str {
        "SAM resource attributes require the Serverless Transform"
    }
    fn description(&self) -> &str {
        "Connectors and IgnoreGlobals are SAM resource attributes \
         that require the Serverless Transform to be declared"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*/Connectors", "Resources/*/IgnoreGlobals"]
    }

    fn validate(
        &self,
        validator: &Validator,
        keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let mut errors = Vec::new();

        // Get the context to access the template
        let ctx = match validator.context() {
            Some(c) => c,
            None => return vec![],
        };

        // Extract the attribute name from the keyword (last segment)
        let attribute = keyword.rsplit('/').next().unwrap_or("");

        // Get the resource name from the path (second element: Resources/<name>/...)
        let resource_name = path.get(1).map(|s| s.as_str()).unwrap_or("");

        // Get the resource type from the template
        let resource_type = ctx
            .template
            .root
            .get("Resources")
            .and_then(|r| r.get(resource_name))
            .and_then(|r| r.get("Type"))
            .and_then(|t| t.as_str())
            .unwrap_or("");

        // Check if the resource type is a Serverless resource
        if !is_serverless_type(resource_type) {
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} is a SAM resource attribute only valid on AWS::Serverless::* resources, \
                     not {:?}",
                    attribute, resource_type
                ),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
            return errors;
        }

        // Check if the SAM transform is declared
        if !is_sam_template(&ctx.template.root) {
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} is a SAM resource attribute that requires \
                     the serverless transform {:?}",
                    attribute, TRANSFORM_SAM
                ),
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }

        // Validate IgnoreGlobals
        if attribute == "IgnoreGlobals" {
            // Check format: must be "*" or an array of strings
            let is_wildcard = matches!(instance, AstNode::String(s) if s.value == "*");
            let is_string_array = matches!(instance, AstNode::Array(arr) if arr.elements.iter().all(|e| e.as_str().is_some()));

            if !is_wildcard && !is_string_array {
                errors.push(ValidationError {
                    rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: "\"IgnoreGlobals\" must be the string \"*\" or an array of strings"
                        .to_string(),
                    path: path.to_vec(),
                    span: instance.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                });
            }

            // Validate key names when IgnoreGlobals is an array
            // Skip validation for "*" (ignores everything, no key check needed)
            if let AstNode::Array(arr) = instance {
                // Get the corresponding Globals section key for this resource type
                if let Some(globals_key) = globals_key_for_resource_type(resource_type) {
                    // Get the actual Globals section from the template
                    if let Some(globals_section) = ctx.template.root.get("Globals") {
                        // Get the properties defined in the Globals section for this resource type
                        if let Some(global_props) = globals_section.get(globals_key) {
                            // Build set of valid keys from the user's Globals section
                            let valid_keys: HashSet<&str> = global_props
                                .as_object()
                                .map(|obj| obj.keys().collect())
                                .unwrap_or_default();

                            // Only validate if there are keys defined in the Globals section
                            if !valid_keys.is_empty() {
                                // Check each entry in IgnoreGlobals
                                for (idx, element) in arr.elements.iter().enumerate() {
                                    if let Some(key) = element.as_str() {
                                        if !valid_keys.contains(key) {
                                            let mut entry_path = path.to_vec();
                                            entry_path.push(idx.to_string());

                                            let mut sorted_keys: Vec<&str> =
                                                valid_keys.iter().copied().collect();
                                            sorted_keys.sort();

                                            errors.push(ValidationError {
                                                rule_id: None,
                                                keyword: format!("cfnLint:{}", self.id()),
                                                message: format!(
                                                    "{:?} is not a valid global property for {:?}. \
                                                     Valid properties are: {:?}",
                                                    key, globals_key, sorted_keys
                                                ),
                                                path: entry_path,
                                                span: element.span(),
                                                unknown: false,
                                                resolved_from_ref: false,
                                                context: vec![],
                                                schema_id: None,
                                            });
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        errors
    }
}

crate::register_cfn_lint_rule!(E3066);

#[cfg(test)]
mod tests {
    use std::sync::Arc;

    use super::*;
    use crate::context::Context;
    use crate::parser;
    use crate::template::Template;

    fn run_validation(yaml: &[u8], resource_name: &str, attribute: &str) -> Vec<ValidationError> {
        let ast = parser::parse(yaml).unwrap();
        let template = Template::from_ast(&ast).unwrap();
        let ctx = Context::new(Arc::new(template));
        let validator = Validator::new_with_context(serde_json::json!({}), Arc::new(ctx));

        let instance = ast
            .get("Resources")
            .unwrap()
            .get(resource_name)
            .unwrap()
            .get(attribute)
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            resource_name.to_string(),
            attribute.to_string(),
        ];
        let keyword = format!("Resources/*/{}", attribute);

        E3066.validate(
            &validator,
            &keyword,
            instance,
            &serde_json::json!({}),
            &path,
        )
    }

    #[test]
    fn test_rule_metadata() {
        assert_eq!(E3066.id(), "E3066");
        assert_eq!(E3066.severity(), Severity::Error);
        assert!(E3066.description().contains("Connectors"));
        assert!(E3066.description().contains("IgnoreGlobals"));
    }

    #[test]
    fn test_connectors_valid_with_transform() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Connectors:
      MyConnector:
        Properties:
          Destination:
            Id: MyBucket
    Properties:
      Runtime: python3.9
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "Connectors");
        assert!(errors.is_empty());
    }

    #[test]
    fn test_connectors_missing_transform() {
        let yaml = br#"
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Connectors:
      MyConnector:
        Properties:
          Destination:
            Id: MyBucket
    Properties:
      Runtime: python3.9
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "Connectors");
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("serverless transform"));
        assert!(errors[0].message.contains("AWS::Serverless-2016-10-31"));
    }

    #[test]
    fn test_connectors_on_non_serverless_resource() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    Connectors:
      MyConnector:
        Properties:
          Destination:
            Id: MyFunction
"#;
        let errors = run_validation(yaml, "MyBucket", "Connectors");
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("AWS::Serverless::*"));
        assert!(errors[0].message.contains("AWS::S3::Bucket"));
    }

    #[test]
    fn test_ignore_globals_star_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals: "*"
    Properties:
      Runtime: python3.9
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert!(errors.is_empty());
    }

    #[test]
    fn test_ignore_globals_array_valid() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Environment
      - Timeout
    Properties:
      Runtime: python3.9
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert!(errors.is_empty());
    }

    #[test]
    fn test_ignore_globals_invalid_string() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals: "Environment"
    Properties:
      Runtime: python3.9
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("must be the string \"*\""));
        assert!(errors[0].message.contains("array of strings"));
    }

    #[test]
    fn test_ignore_globals_missing_transform() {
        let yaml = br#"
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals: "*"
    Properties:
      Runtime: python3.9
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("serverless transform"));
    }

    #[test]
    fn test_ignore_globals_on_non_serverless_resource() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
    IgnoreGlobals: "*"
"#;
        let errors = run_validation(yaml, "MyBucket", "IgnoreGlobals");
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("AWS::Serverless::*"));
    }

    #[test]
    fn test_transform_in_array() {
        let yaml = br#"
Transform:
  - AWS::Serverless-2016-10-31
  - AWS::LanguageExtensions
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Connectors:
      MyConnector:
        Properties:
          Destination:
            Id: MyBucket
    Properties:
      Runtime: python3.9
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "Connectors");
        assert!(errors.is_empty());
    }

    // ===== IgnoreGlobals key validation tests =====

    #[test]
    fn test_ignore_globals_valid_key_in_globals() {
        // Valid: IgnoreGlobals lists "Timeout" which exists in Globals.Function
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Timeout
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_multiple_valid_keys() {
        // Valid: Both keys exist in Globals.Function
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
    MemorySize: 256
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Timeout
      - Runtime
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_invalid_key_typo() {
        // Invalid: "Timeot" is a typo (should be "Timeout")
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Timeot
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert_eq!(errors.len(), 1, "Expected 1 error, got: {:?}", errors);
        assert!(
            errors[0].message.contains("\"Timeot\""),
            "Error should mention the bad key: {:?}",
            errors[0].message
        );
        assert!(
            errors[0].message.contains("not a valid global property"),
            "Error should say 'not a valid global property': {:?}",
            errors[0].message
        );
        assert!(
            errors[0].message.contains("Function"),
            "Error should mention the Globals section: {:?}",
            errors[0].message
        );
        // Path should point to the specific array index
        assert_eq!(
            errors[0].path,
            vec!["Resources", "MyFunction", "IgnoreGlobals", "0"]
        );
    }

    #[test]
    fn test_ignore_globals_invalid_key_not_in_globals() {
        // Invalid: "Environment" is a valid Function property but not defined in Globals.Function
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Environment
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert_eq!(errors.len(), 1, "Expected 1 error, got: {:?}", errors);
        assert!(errors[0].message.contains("\"Environment\""));
        assert!(errors[0].message.contains("not a valid global property"));
    }

    #[test]
    fn test_ignore_globals_mixed_valid_and_invalid_keys() {
        // Mixed: "Runtime" is valid, "InvalidKey" is not
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
    Runtime: python3.9
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - InvalidKey
      - Runtime
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert_eq!(errors.len(), 1, "Expected 1 error, got: {:?}", errors);
        assert!(errors[0].message.contains("\"InvalidKey\""));
        // Path should point to index 0 (the invalid key)
        assert_eq!(
            errors[0].path,
            vec!["Resources", "MyFunction", "IgnoreGlobals", "0"]
        );
    }

    #[test]
    fn test_ignore_globals_multiple_invalid_keys() {
        // Multiple invalid keys should each produce an error
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Typo1
      - Typo2
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert_eq!(errors.len(), 2, "Expected 2 errors, got: {:?}", errors);
        assert!(errors[0].message.contains("\"Typo1\""));
        assert!(errors[1].message.contains("\"Typo2\""));
    }

    #[test]
    fn test_ignore_globals_wildcard_no_key_validation() {
        // "*" should not trigger key validation even with invalid-looking Globals
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Timeout: 30
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals: "*"
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert!(
            errors.is_empty(),
            "Expected no errors for '*', got: {:?}",
            errors
        );
    }

    #[test]
    fn test_ignore_globals_no_globals_section() {
        // No Globals section means no validation of keys
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Timeout
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        // No error: if there's no Globals section, there's nothing to ignore
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_no_matching_globals_section_for_type() {
        // Globals.Api exists but resource is Function - no validation
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Api:
    TracingEnabled: true
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - Timeout
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        // No error: there's no Globals.Function section to validate against
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_api_resource_valid() {
        // Valid: IgnoreGlobals on Api resource with valid key
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Api:
    TracingEnabled: true
    Name: MyGlobalApi
Resources:
  MyApi:
    Type: AWS::Serverless::Api
    IgnoreGlobals:
      - TracingEnabled
    Properties:
      StageName: prod
"#;
        let errors = run_validation(yaml, "MyApi", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_api_resource_invalid() {
        // Invalid: IgnoreGlobals on Api resource with invalid key
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Api:
    TracingEnabled: true
Resources:
  MyApi:
    Type: AWS::Serverless::Api
    IgnoreGlobals:
      - TracingEnable
    Properties:
      StageName: prod
"#;
        let errors = run_validation(yaml, "MyApi", "IgnoreGlobals");
        assert_eq!(errors.len(), 1, "Expected 1 error, got: {:?}", errors);
        assert!(errors[0].message.contains("\"TracingEnable\""));
        assert!(errors[0].message.contains("\"Api\""));
    }

    #[test]
    fn test_ignore_globals_http_api_resource() {
        // Valid: IgnoreGlobals on HttpApi resource
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  HttpApi:
    Auth: {}
Resources:
  MyHttpApi:
    Type: AWS::Serverless::HttpApi
    IgnoreGlobals:
      - Auth
    Properties: {}
"#;
        let errors = run_validation(yaml, "MyHttpApi", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_shows_valid_keys_in_error() {
        // Error message should list valid keys
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  Function:
    Runtime: python3.9
    Timeout: 30
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    IgnoreGlobals:
      - InvalidKey
    Properties:
      Handler: index.handler
"#;
        let errors = run_validation(yaml, "MyFunction", "IgnoreGlobals");
        assert_eq!(errors.len(), 1);
        // Should list valid keys (sorted alphabetically)
        assert!(
            errors[0].message.contains("Runtime"),
            "Error should list valid keys: {:?}",
            errors[0].message
        );
        assert!(
            errors[0].message.contains("Timeout"),
            "Error should list valid keys: {:?}",
            errors[0].message
        );
    }

    #[test]
    fn test_ignore_globals_state_machine_resource() {
        // Valid: IgnoreGlobals on StateMachine resource
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  StateMachine:
    PropagateTags: true
Resources:
  MyStateMachine:
    Type: AWS::Serverless::StateMachine
    IgnoreGlobals:
      - PropagateTags
    Properties:
      Name: MyMachine
"#;
        let errors = run_validation(yaml, "MyStateMachine", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_simple_table_resource() {
        // Valid: IgnoreGlobals on SimpleTable resource
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  SimpleTable:
    SSESpecification: {}
Resources:
  MyTable:
    Type: AWS::Serverless::SimpleTable
    IgnoreGlobals:
      - SSESpecification
    Properties:
      TableName: MyTable
"#;
        let errors = run_validation(yaml, "MyTable", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_layer_version_resource() {
        // Valid: IgnoreGlobals on LayerVersion resource
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  LayerVersion:
    PublishLambdaVersion: true
Resources:
  MyLayer:
    Type: AWS::Serverless::LayerVersion
    IgnoreGlobals:
      - PublishLambdaVersion
    Properties:
      LayerName: MyLayer
"#;
        let errors = run_validation(yaml, "MyLayer", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_capacity_provider_resource() {
        // Valid: IgnoreGlobals on CapacityProvider resource
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  CapacityProvider:
    PropagateTags: true
Resources:
  MyCapacityProvider:
    Type: AWS::Serverless::CapacityProvider
    IgnoreGlobals:
      - PropagateTags
    Properties:
      Name: MyProvider
"#;
        let errors = run_validation(yaml, "MyCapacityProvider", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }

    #[test]
    fn test_ignore_globals_websocket_api_resource() {
        // Valid: IgnoreGlobals on WebSocketApi resource
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Globals:
  WebSocketApi:
    PropagateTags: true
Resources:
  MyWebSocketApi:
    Type: AWS::Serverless::WebSocketApi
    IgnoreGlobals:
      - PropagateTags
    Properties:
      StageName: prod
"#;
        let errors = run_validation(yaml, "MyWebSocketApi", "IgnoreGlobals");
        assert!(errors.is_empty(), "Expected no errors, got: {:?}", errors);
    }
}
