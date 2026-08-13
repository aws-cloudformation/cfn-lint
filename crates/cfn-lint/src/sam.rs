//! SAM implicit resource injection for Ref/GetAtt validation.
//!
//! When SAM transforms a template, it generates implicit resources that don't
//! appear in the source template but are valid Ref/GetAtt targets. This module
//! computes those synthetic resources so Ref/GetAtt validation can accept them
//! without false positives.
//!
//! The injected resources have no source spans and are used ONLY for target
//! resolution — they must never appear in diagnostics.

use crate::ast::AstNode;

/// A synthetic resource injected for SAM implicit resource resolution.
/// These resources exist only for Ref/GetAtt target validation.
#[derive(Debug, Clone)]
pub struct SyntheticResource {
    /// Logical ID of the synthetic resource
    pub logical_id: String,
    /// CloudFormation resource type
    pub resource_type: String,
}

/// Collect all SAM implicit resources from a template's Resources section.
///
/// This mirrors Python cfn-lint's `_inject_sam_implicit_resources` function.
/// For each SAM resource, we inject the synthetic resources SAM would generate:
/// - Per-Function IAM Role (`<Id>Role`)
/// - Lambda Version/Alias when AutoPublishAlias or DeploymentPreference
/// - Lambda Url when FunctionUrlConfig
/// - CodeDeploy resources when DeploymentPreference
/// - API/HttpApi Stage/Deployment
/// - StateMachine role
/// - Implicit ServerlessRestApi/ServerlessHttpApi when functions have events
pub fn collect_sam_implicit_resources(root: &AstNode) -> Vec<SyntheticResource> {
    let resources = match root.get("Resources").and_then(|r| r.as_object()) {
        Some(r) => r,
        None => return vec![],
    };

    let mut synthetic = Vec::new();
    let mut needs_rest_api = false;
    let mut needs_http_api = false;

    for (resource_id, resource_node) in resources.iter() {
        let resource_obj = match resource_node.as_object() {
            Some(o) => o,
            None => continue,
        };

        let resource_type = match resource_obj.get("Type").and_then(|t| t.as_str()) {
            Some(t) => t,
            None => continue,
        };

        let props = resource_obj.get("Properties").and_then(|p| p.as_object());

        match resource_type {
            "AWS::Serverless::Function" => {
                inject_function_resources(
                    resource_id,
                    props,
                    &mut synthetic,
                    &mut needs_rest_api,
                    &mut needs_http_api,
                );
            }
            "AWS::Serverless::StateMachine" => {
                inject_state_machine_resources(resource_id, props, &mut synthetic);
            }
            "AWS::Serverless::Api" => {
                inject_api_resources(resource_id, props, &mut synthetic);
            }
            "AWS::Serverless::HttpApi" => {
                inject_http_api_resources(resource_id, &mut synthetic);
            }
            _ => {}
        }
    }

    // Inject implicit APIs if needed
    if needs_rest_api {
        inject_if_missing(&mut synthetic, "ServerlessRestApi", "AWS::Serverless::Api");
        inject_if_missing(
            &mut synthetic,
            "ServerlessRestApiStage",
            "AWS::ApiGateway::Stage",
        );
    }

    if needs_http_api {
        inject_if_missing(
            &mut synthetic,
            "ServerlessHttpApi",
            "AWS::Serverless::HttpApi",
        );
        inject_if_missing(
            &mut synthetic,
            "ServerlessHttpApiStage",
            "AWS::ApiGatewayV2::Stage",
        );
    }

    synthetic
}

/// Inject a synthetic resource if it doesn't already exist in the list.
fn inject_if_missing(
    synthetic: &mut Vec<SyntheticResource>,
    logical_id: &str,
    resource_type: &str,
) {
    if !synthetic.iter().any(|s| s.logical_id == logical_id) {
        synthetic.push(SyntheticResource {
            logical_id: logical_id.to_string(),
            resource_type: resource_type.to_string(),
        });
    }
}

/// Inject synthetic resources for AWS::Serverless::Function.
fn inject_function_resources(
    resource_id: &str,
    props: Option<&crate::ast::ObjectNode>,
    synthetic: &mut Vec<SyntheticResource>,
    needs_rest_api: &mut bool,
    needs_http_api: &mut bool,
) {
    // Function without explicit Role gets a generated Role
    if props.is_none_or(|p| !p.contains_key("Role")) {
        synthetic.push(SyntheticResource {
            logical_id: format!("{}Role", resource_id),
            resource_type: "AWS::IAM::Role".to_string(),
        });
    }

    let props = match props {
        Some(p) => p,
        None => return,
    };

    // Version/Alias when AutoPublishAlias or DeploymentPreference
    let has_auto_publish = props.contains_key("AutoPublishAlias");
    let has_deployment_pref = props.contains_key("DeploymentPreference");

    if has_auto_publish || has_deployment_pref {
        // SAM generates dotted logical IDs for Version/Alias
        synthetic.push(SyntheticResource {
            logical_id: format!("{}.Version", resource_id),
            resource_type: "AWS::Lambda::Version".to_string(),
        });
        synthetic.push(SyntheticResource {
            logical_id: format!("{}.Alias", resource_id),
            resource_type: "AWS::Lambda::Alias".to_string(),
        });
    }

    // Url when FunctionUrlConfig is set
    if props.contains_key("FunctionUrlConfig") {
        synthetic.push(SyntheticResource {
            logical_id: format!("{}Url", resource_id),
            resource_type: "AWS::Lambda::Url".to_string(),
        });
    }

    // DeploymentPreference generates CodeDeploy resources
    if let Some(dp_node) = props.get("DeploymentPreference") {
        let dp_enabled = match dp_node.as_object() {
            Some(dp_obj) => dp_obj
                .get("Enabled")
                .and_then(|e| e.as_bool())
                .unwrap_or(true),
            None => dp_node.as_bool().unwrap_or(true),
        };

        if dp_enabled {
            inject_if_missing(
                synthetic,
                "ServerlessDeploymentApplication",
                "AWS::CodeDeploy::Application",
            );
            synthetic.push(SyntheticResource {
                logical_id: format!("{}DeploymentGroup", resource_id),
                resource_type: "AWS::CodeDeploy::DeploymentGroup".to_string(),
            });

            // CodeDeploy service role if not specified
            let has_dp_role = dp_node
                .as_object()
                .is_some_and(|dp| dp.contains_key("Role"));
            if !has_dp_role {
                inject_if_missing(synthetic, "CodeDeployServiceRole", "AWS::IAM::Role");
            }
        }
    }

    // Per-event permissions and implicit API detection
    if let Some(events) = props.get("Events").and_then(|e| e.as_object()) {
        for (event_name, event_node) in events.iter() {
            // Lambda permission per event
            synthetic.push(SyntheticResource {
                logical_id: format!("{}{}Permission", resource_id, event_name),
                resource_type: "AWS::Lambda::Permission".to_string(),
            });

            // Check for implicit API needs
            if let Some(event_obj) = event_node.as_object() {
                let event_type = event_obj.get("Type").and_then(|t| t.as_str());
                let event_props = event_obj.get("Properties").and_then(|p| p.as_object());

                match event_type {
                    Some("Api") => {
                        let has_rest_api_id =
                            event_props.is_some_and(|ep| ep.contains_key("RestApiId"));
                        if !has_rest_api_id {
                            *needs_rest_api = true;
                        }
                    }
                    Some("HttpApi") => {
                        let has_api_id = event_props.is_some_and(|ep| ep.contains_key("ApiId"));
                        if !has_api_id {
                            *needs_http_api = true;
                        }
                    }
                    _ => {}
                }
            }
        }
    }
}

/// Inject synthetic resources for AWS::Serverless::StateMachine.
fn inject_state_machine_resources(
    resource_id: &str,
    props: Option<&crate::ast::ObjectNode>,
    synthetic: &mut Vec<SyntheticResource>,
) {
    // StateMachine without explicit Role gets a generated Role
    if props.is_none_or(|p| !p.contains_key("Role")) {
        synthetic.push(SyntheticResource {
            logical_id: format!("{}Role", resource_id),
            resource_type: "AWS::IAM::Role".to_string(),
        });
    }
}

/// Inject synthetic resources for AWS::Serverless::Api.
fn inject_api_resources(
    resource_id: &str,
    props: Option<&crate::ast::ObjectNode>,
    synthetic: &mut Vec<SyntheticResource>,
) {
    // Stage is always generated
    synthetic.push(SyntheticResource {
        logical_id: format!("{}Stage", resource_id),
        resource_type: "AWS::ApiGateway::Stage".to_string(),
    });

    // Deployment is always generated
    synthetic.push(SyntheticResource {
        logical_id: format!("{}Deployment", resource_id),
        resource_type: "AWS::ApiGateway::Deployment".to_string(),
    });

    if let Some(p) = props {
        // Domain when Domain is set
        if p.contains_key("Domain") {
            synthetic.push(SyntheticResource {
                logical_id: format!("{}DomainName", resource_id),
                resource_type: "AWS::ApiGateway::DomainName".to_string(),
            });
        }

        // UsagePlan when Auth is set
        if p.contains_key("Auth") {
            synthetic.push(SyntheticResource {
                logical_id: format!("{}UsagePlan", resource_id),
                resource_type: "AWS::ApiGateway::UsagePlan".to_string(),
            });
        }
    }
}

/// Inject synthetic resources for AWS::Serverless::HttpApi.
fn inject_http_api_resources(resource_id: &str, synthetic: &mut Vec<SyntheticResource>) {
    synthetic.push(SyntheticResource {
        logical_id: format!("{}Stage", resource_id),
        resource_type: "AWS::ApiGatewayV2::Stage".to_string(),
    });
}

/// Get a set of all valid Ref targets including SAM implicit resources.
/// Returns (valid_refs, module_prefixes) where module_prefixes are logical IDs
/// that support dotted sub-resource refs (MODULE and Serverless types).
pub fn get_sam_valid_refs(
    template_resources: &std::collections::HashMap<String, crate::template::Resource>,
    template_parameters: &std::collections::HashMap<String, crate::template::Parameter>,
    synthetic_resources: &[SyntheticResource],
) -> (Vec<String>, Vec<String>) {
    let mut valid_refs = Vec::new();
    let mut module_prefixes = Vec::new();

    // Add all template resources
    for (name, resource) in template_resources {
        valid_refs.push(name.clone());
        if resource.resource_type.ends_with("::MODULE")
            || resource.resource_type.starts_with("AWS::Serverless::")
        {
            module_prefixes.push(name.clone());
        }
    }

    // Add all parameters
    for name in template_parameters.keys() {
        valid_refs.push(name.clone());
    }

    // Add synthetic resources
    for sr in synthetic_resources {
        valid_refs.push(sr.logical_id.clone());
        // Synthetic Serverless resources also support prefix matching
        if sr.resource_type.starts_with("AWS::Serverless::") {
            module_prefixes.push(sr.logical_id.clone());
        }
    }

    (valid_refs, module_prefixes)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_function_without_role_gets_implicit_role() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(
            synthetic
                .iter()
                .any(|s| s.logical_id == "MyFunctionRole" && s.resource_type == "AWS::IAM::Role"),
            "Expected MyFunctionRole in {:?}",
            synthetic
        );
    }

    #[test]
    fn test_function_with_role_no_implicit_role() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      Role: !GetAtt MyRole.Arn
  MyRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument: {}
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(
            !synthetic.iter().any(|s| s.logical_id == "MyFunctionRole"),
            "Should not have MyFunctionRole when Role is specified"
        );
    }

    #[test]
    fn test_function_auto_publish_alias() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      AutoPublishAlias: live
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "MyFunction.Version"));
        assert!(synthetic.iter().any(|s| s.logical_id == "MyFunction.Alias"));
    }

    #[test]
    fn test_function_deployment_preference() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      DeploymentPreference:
        Type: Linear10PercentEvery1Minute
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "ServerlessDeploymentApplication"));
        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "MyFunctionDeploymentGroup"));
        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "CodeDeployServiceRole"));
        // Also gets Version/Alias
        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "MyFunction.Version"));
    }

    #[test]
    fn test_function_url_config() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      FunctionUrlConfig:
        AuthType: NONE
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(synthetic.iter().any(|s| s.logical_id == "MyFunctionUrl"));
    }

    #[test]
    fn test_function_api_event_implicit_rest_api() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /hello
            Method: get
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        // Implicit ServerlessRestApi and stage
        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "ServerlessRestApi"));
        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "ServerlessRestApiStage"));
        // Permission per event
        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "MyFunctionApiEventPermission"));
    }

    #[test]
    fn test_function_http_api_event_implicit_http_api() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      Events:
        HttpEvent:
          Type: HttpApi
          Properties:
            Path: /hello
            Method: get
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "ServerlessHttpApi"));
        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "ServerlessHttpApiStage"));
    }

    #[test]
    fn test_explicit_api_no_implicit() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.9
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /hello
            Method: get
            RestApiId: !Ref MyApi
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        // Should NOT have implicit ServerlessRestApi since RestApiId is specified
        assert!(
            !synthetic
                .iter()
                .any(|s| s.logical_id == "ServerlessRestApi"),
            "Should not inject implicit API when RestApiId is specified"
        );
        // But MyApi's Stage should be there
        assert!(synthetic.iter().any(|s| s.logical_id == "MyApiStage"));
    }

    #[test]
    fn test_api_resources() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Domain:
        DomainName: api.example.com
      Auth:
        UsagePlan:
          UsagePlanName: MyPlan
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(synthetic.iter().any(|s| s.logical_id == "MyApiStage"));
        assert!(synthetic.iter().any(|s| s.logical_id == "MyApiDeployment"));
        assert!(synthetic.iter().any(|s| s.logical_id == "MyApiDomainName"));
        assert!(synthetic.iter().any(|s| s.logical_id == "MyApiUsagePlan"));
    }

    #[test]
    fn test_http_api_resources() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyHttpApi:
    Type: AWS::Serverless::HttpApi
    Properties:
      StageName: prod
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(synthetic.iter().any(|s| s.logical_id == "MyHttpApiStage"));
    }

    #[test]
    fn test_state_machine_implicit_role() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyStateMachine:
    Type: AWS::Serverless::StateMachine
    Properties:
      Definition:
        StartAt: Hello
        States:
          Hello:
            Type: Pass
            End: true
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(synthetic
            .iter()
            .any(|s| s.logical_id == "MyStateMachineRole"));
    }

    #[test]
    fn test_non_sam_template_no_synthetic() {
        let yaml = br#"
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  MyBucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let synthetic = collect_sam_implicit_resources(&ast);

        assert!(
            synthetic.is_empty(),
            "Non-SAM template should have no synthetic resources"
        );
    }
}
