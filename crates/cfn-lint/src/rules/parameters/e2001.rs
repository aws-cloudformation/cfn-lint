use std::sync::LazyLock;

use crate::ast::AstNode;
use crate::engine::format_node_short;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::Validator;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

static SCHEMA: LazyLock<serde_json::Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("../../../data/schemas/other/parameters/configuration.json"))
        .unwrap_or_default()
});

/// E2001: Parameters have appropriate properties.
pub struct E2001;

impl CfnLintRule for E2001 {
    fn id(&self) -> &str {
        "E2001"
    }
    fn short_description(&self) -> &str {
        "Parameters have appropriate properties"
    }
    fn description(&self) -> &str {
        "Making sure the parameters are properly configured"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }
    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let params = match root.get("Parameters") {
            Some(n) => n,
            None => return vec![],
        };

        let mut issues = Vec::new();

        // Schema-based validation
        let validator = Validator::new(SCHEMA.clone());
        let base_path = vec!["Parameters".to_string()];
        issues.extend(
            validator
                .validate(params, &SCHEMA, &base_path)
                .into_iter()
                .filter(|e| !e.unknown)
                .map(|err| {
                    let rule_id = match err.keyword.as_str() {
                        "maxProperties" => "E2010",
                        "propertyNames" | "maxLength" | "minLength" => "E2011",
                        "additionalProperties" => "E2001",
                        "type" => "E2001",
                        _ => "E2001",
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
                }),
        );

        // Check for function nodes in parameter properties that expect strings
        // (Type, Default, etc.) - functions are not valid in parameter definitions
        if let Some(obj) = params.as_object() {
            for (param_name, param_node) in obj.iter() {
                if let Some(param_obj) = param_node.as_object() {
                    for (key, val) in param_obj.iter() {
                        if val.as_function().is_some() {
                            issues.push(ValidationError {
                                rule_id: Some("E2001".to_string()),
                                message: format!(
                                    "{} is not of type 'string'",
                                    format_node_short(val)
                                ),
                                path: vec![
                                    "Parameters".to_string(),
                                    param_name.to_string(),
                                    key.to_string(),
                                ],
                                span: val.span(),
                                keyword: String::new(),
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

        issues
    }
}

crate::register_cfn_lint_rule!(E2001);
