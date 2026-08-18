use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::template::Template;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!(
        "../../../../data/schemas/other/resources/configuration.json"
    ))
    .unwrap_or_default()
});

/// E3001: Basic CloudFormation Resource Check.
///
/// Validates the Resources section against its configuration schema:
/// - Resource names match pattern ^[a-zA-Z0-9]+$
/// - Max 500 resources
/// - Each resource has valid top-level keys (Type, Properties, Condition, etc.)
///
/// For AWS::Serverless::* resources, unknown resource-level attributes are
/// reported as W3001 (warning) instead of E3001 (error), because the SAM
/// transform silently drops them — the template still deploys but the value
/// is lost.
pub struct E3001;

/// Check if the error represents an unknown resource-level attribute on a SAM resource.
///
/// Returns true when:
/// - The error is from `additionalProperties` keyword
/// - The path has exactly 2 elements: ["Resources", "<ResourceName>"]
///   (the error path points to the resource, the unknown key is in the message)
/// - The resource's Type starts with "AWS::Serverless::"
fn is_serverless_additional_property(err: &ValidationError, resources: &AstNode) -> bool {
    if err.keyword != "additionalProperties" {
        return false;
    }

    // Path must be exactly ["Resources", "ResourceName"]
    // This indicates an error at the resource level (additionalProperties on resource config)
    if err.path.len() != 2 {
        return false;
    }

    if err.path.first().map(|s| s.as_str()) != Some("Resources") {
        return false;
    }

    // Get the resource name from the path
    let resource_name = &err.path[1];

    // Look up the resource in the AST to check its Type
    let resource = match resources.get(resource_name) {
        Some(r) => r,
        None => return false,
    };

    // Get the Type property
    let resource_type = match resource.get("Type").and_then(|t| t.as_str()) {
        Some(t) => t,
        None => return false,
    };

    resource_type.starts_with("AWS::Serverless::")
}

impl CfnLintRule for E3001 {
    fn id(&self) -> &str {
        "E3001"
    }
    fn short_description(&self) -> &str {
        "Validate basic resource configuration"
    }
    fn description(&self) -> &str {
        "Validates basic CloudFormation resource configuration"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }
    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        _template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        let resources = match root.get("Resources") {
            Some(r) => r,
            None => return vec![],
        };

        let validator = Validator::new_strict(SCHEMA.clone());
        let base_path = vec!["Resources".to_string()];

        validator
            .validate(resources, &SCHEMA, &base_path)
            .into_iter()
            .filter(|e| !e.unknown)
            .map(|err| {
                // Check if this is a SAM resource-level additional property
                if is_serverless_additional_property(&err, resources) {
                    // Convert to W3001 warning with a SAM-specific message
                    let message = err.message.replace(
                        "Additional properties are not allowed",
                        "Additional resource properties are ignored by the SAM transform",
                    );
                    return ValidationError {
                        rule_id: Some("W3001".to_string()),
                        message,
                        path: err.path,
                        span: err.span,
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    };
                }

                let rule_id = match err.keyword.as_str() {
                    "maxProperties" => "E3010",
                    "propertyNames" | "maxLength" | "minLength" => "E3011",
                    "patternProperties" | "additionalProperties" => "E3001",
                    _ => "E3001",
                };
                ValidationError {
                    rule_id: Some(rule_id.to_string()),
                    message: err.message,
                    path: err.path,
                    span: err.span,
                    keyword: String::new(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }
            })
            .collect()
    }
}

crate::register_cfn_lint_rule!(E3001);
