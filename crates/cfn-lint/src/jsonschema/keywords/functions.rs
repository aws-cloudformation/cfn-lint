use std::collections::HashMap;
use std::sync::LazyLock;

use super::super::{ValidationError, Validator};
use super::helpers::{ast_to_json_string, err, unknown_err};
use crate::ast::AstNode;

static FUNCTION_SCHEMAS: LazyLock<HashMap<&'static str, serde_json::Value>> = LazyLock::new(|| {
    let entries: &[(&str, &str)] = &[
        (
            "Fn::If",
            include_str!("../../../data/schemas/other/functions/if.json"),
        ),
        (
            "Fn::GetAtt",
            include_str!("../../../data/schemas/other/functions/getatt.json"),
        ),
        (
            "Fn::Sub",
            include_str!("../../../data/schemas/other/functions/sub.json"),
        ),
        (
            "Fn::Join",
            include_str!("../../../data/schemas/other/functions/join.json"),
        ),
        (
            "Fn::Select",
            include_str!("../../../data/schemas/other/functions/select.json"),
        ),
        (
            "Fn::FindInMap",
            include_str!("../../../data/schemas/other/functions/findinmap.json"),
        ),
        (
            "Fn::Base64",
            include_str!("../../../data/schemas/other/functions/base64.json"),
        ),
        (
            "Fn::ImportValue",
            include_str!("../../../data/schemas/other/functions/importvalue.json"),
        ),
        (
            "Fn::GetAZs",
            include_str!("../../../data/schemas/other/functions/getazs.json"),
        ),
        (
            "Fn::Split",
            include_str!("../../../data/schemas/other/functions/split.json"),
        ),
        (
            "Fn::Cidr",
            include_str!("../../../data/schemas/other/functions/cidr.json"),
        ),
        (
            "Fn::Length",
            include_str!("../../../data/schemas/other/functions/length.json"),
        ),
        (
            "Fn::ToJsonString",
            include_str!("../../../data/schemas/other/functions/tojsonstring.json"),
        ),
        (
            "Fn::GetStackOutput",
            include_str!("../../../data/schemas/other/functions/getstackoutput.json"),
        ),
        (
            "Fn::Equals",
            include_str!("../../../data/schemas/other/functions/equals.json"),
        ),
        (
            "Fn::And",
            include_str!("../../../data/schemas/other/functions/and.json"),
        ),
        (
            "Fn::Or",
            include_str!("../../../data/schemas/other/functions/or.json"),
        ),
        (
            "Fn::Not",
            include_str!("../../../data/schemas/other/functions/not.json"),
        ),
        (
            "Condition",
            include_str!("../../../data/schemas/other/functions/condition.json"),
        ),
        (
            "Ref",
            include_str!("../../../data/schemas/other/functions/ref.json"),
        ),
    ];
    entries
        .iter()
        .map(|(k, v)| (*k, serde_json::from_str(v).unwrap()))
        .collect()
});

fn to_equals_str(node: &AstNode) -> Option<String> {
    match node {
        AstNode::String(s) => Some(s.value.clone()),
        AstNode::Number(n) => Some(n.value.to_string()),
        AstNode::Bool(b) => Some(if b.value {
            "true".to_string()
        } else {
            "false".to_string()
        }),
        _ => None,
    }
}

pub fn validate_fn_unknown(
    _validator: &Validator,
    node: &AstNode,
    _constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    vec![unknown_err("function", path, node)]
}

pub fn validate_fn_getstackoutput(
    validator: &Validator,
    node: &AstNode,
    _constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let func = match node.as_function() {
        Some(f) => f,
        None => return vec![unknown_err("fn_getstackoutput", path, node)],
    };
    let mut errors = validate_function_structure(validator, &func.name, &func.args, path);
    for e in &mut errors {
        e.keyword = "fn_getstackoutput".to_string();
    }
    if !errors.is_empty() {
        return errors;
    }
    vec![unknown_err("fn_getstackoutput", path, node)]
}

pub fn validate_fn_structure_only(
    validator: &Validator,
    node: &AstNode,
    _constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let func = match node.as_function() {
        Some(f) => f,
        None => return vec![unknown_err("function", path, node)],
    };
    let rule_id = match func.name.as_str() {
        "Fn::Equals" => "E8003",
        "Fn::And" => "E8004",
        "Fn::Not" => "E8005",
        "Fn::Or" => "E8006",
        "Condition" => "E8007",
        _ => "E8001",
    };
    let mut errors = validate_function_structure(validator, &func.name, &func.args, path);
    let has_structural_errors = !errors.is_empty();
    for e in &mut errors {
        e.keyword = rule_id.to_string();
    }

    if func.name == "Fn::Equals" {
        if let Some(arr) = func.args.as_array() {
            if arr.elements.len() == 2 {
                let a = &arr.elements[0];
                let b = &arr.elements[1];
                let a_json = ast_to_json_string(a);
                let b_json = ast_to_json_string(b);
                if a_json == b_json {
                    errors.push(err(
                        "W8003",
                        format!("{:?} will always return True or False", [&a_json, &b_json]),
                        path,
                        node,
                    ));
                } else {
                    let a_scalar = to_equals_str(a);
                    let b_scalar = to_equals_str(b);
                    if let (Some(av), Some(bv)) = (&a_scalar, &b_scalar) {
                        if av == bv {
                            errors.push(err(
                                "W8003",
                                format!("{:?} will always return True", [&a_json, &b_json]),
                                path,
                                node,
                            ));
                        } else {
                            errors.push(err(
                                "W8003",
                                format!("{:?} will always return False", [&a_json, &b_json]),
                                path,
                                node,
                            ));
                        }
                    }
                }
            }
        }
    }

    if !has_structural_errors {
        errors.push(unknown_err("function", path, node));
    }
    errors
}

pub fn validate_dynamic_reference(
    validator: &Validator,
    node: &AstNode,
    _constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    use regex::Regex;
    use std::sync::LazyLock;

    static RE_DYN_REF: LazyLock<Regex> =
        LazyLock::new(|| Regex::new(r"\{\{resolve:([^}]+)\}\}").unwrap());

    let s = match node.as_str() {
        Some(s) => s,
        None => return vec![unknown_err("dynamicReference", path, node)],
    };

    let mut errors = Vec::new();

    for cap in RE_DYN_REF.captures_iter(s) {
        let inner = &cap[1];
        let parts: Vec<&str> = inner.split(':').collect();
        if parts.is_empty() {
            continue;
        }

        let service = parts[0];

        match service {
            "ssm" => {
                // E1052: SSM allowed in Resources/Properties, Resources/Metadata,
                // Outputs/Value, Parameters/Default, Parameters/AllowedValues
                if !is_valid_ssm_location(path) {
                    errors.push(ValidationError {
                        keyword: "E1052".to_string(),
                        message: format!(
                            "Dynamic reference '{}' to SSM parameters are not allowed here",
                            s
                        ),
                        path: path.to_vec(),
                        span: node.span(),
                        ..Default::default()
                    });
                }
            }
            "ssm-secure" => {
                // E1027: ssm-secure only allowed in specific resource properties
                if !is_valid_secure_string_location(path) {
                    errors.push(ValidationError {
                        keyword: "E1027".to_string(),
                        message: format!(
                            "Dynamic reference '{}' to SSM secure strings can only be used in supported resource properties",
                            s
                        ),
                        path: path.to_vec(),
                        span: node.span(),
                        ..Default::default()
                    });
                }
            }
            "secretsmanager" => {
                // E1051: SecretsManager only in resource properties or parameter defaults
                if !is_valid_secrets_manager_location(path) {
                    errors.push(ValidationError {
                        keyword: "E1051".to_string(),
                        message: format!(
                            "Dynamic reference '{}' to secrets manager can only be used in resource properties",
                            s
                        ),
                        path: path.to_vec(),
                        span: node.span(),
                        ..Default::default()
                    });
                }

                // W1051: Check if used where an ARN is expected
                let arn_fields = [
                    "SecretArn",
                    "SecretARN",
                    "SecretsManagerSecretId",
                    "SecretsManagerOracleAsmSecretId",
                    "SecretsManagerSecurityDbEncryptionSecretId",
                ];
                if path.iter().any(|p| arn_fields.contains(&p.as_str())) {
                    errors.push(ValidationError {
                        keyword: "W1051".to_string(),
                        message: format!(
                            "Dynamic reference '{}' to secrets manager when the field expects the ARN to the secret and not the secret value",
                            s
                        ),
                        path: path.to_vec(),
                        span: node.span(),
                        ..Default::default()
                    });
                }
            }
            _ => {}
        }
    }

    if errors.is_empty() {
        vec![unknown_err("dynamicReference", path, node)]
    } else {
        errors
    }
}

fn is_valid_ssm_location(path: &[String]) -> bool {
    if path.len() < 3 {
        return false;
    }
    match path[0].as_str() {
        "Resources" => path.len() >= 3 && (path[2] == "Properties" || path[2] == "Metadata"),
        "Outputs" => path.len() >= 3 && path[2] == "Value",
        "Parameters" => path.len() >= 3 && (path[2] == "Default" || path[2] == "AllowedValues"),
        _ => false,
    }
}

fn is_valid_secrets_manager_location(path: &[String]) -> bool {
    if path.len() < 3 {
        return false;
    }
    match path[0].as_str() {
        "Resources" => path[2] == "Properties",
        "Parameters" => path[2] == "Default",
        _ => false,
    }
}

fn is_valid_secure_string_location(path: &[String]) -> bool {
    if path.len() < 3 {
        return false;
    }
    if path[0] != "Resources" || path[2] != "Properties" {
        return false;
    }
    true
}

pub fn validate_dynamic_validation(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let obj = match constraint.as_object() {
        Some(o) => o,
        None => return vec![],
    };
    let ctx = match &validator.context {
        Some(c) => c,
        None => return vec![],
    };

    if let Some(context_source) = obj.get("context").and_then(|v| v.as_str()) {
        let collection: Vec<String> = match context_source {
            "conditions" => ctx.template.conditions.keys().cloned().collect(),
            _ => return vec![],
        };
        let enum_schema = serde_json::json!({"enum": collection});
        return validator.validate_schema(node, &enum_schema, path);
    }

    if let Some(transform) = obj.get("transformCheck").and_then(|v| v.as_str()) {
        let transform_node = ctx.template.root.get("Transform");
        let has_transform = match transform_node {
            Some(t) if t.as_str().is_some() => t.as_str().unwrap() == transform,
            Some(t) if t.as_array().is_some() => t
                .as_array()
                .unwrap()
                .elements
                .iter()
                .any(|e| e.as_str() == Some(transform)),
            _ => false,
        };
        if !has_transform {
            return vec![err(
                "dynamicValidation",
                format!("Transform '{}' not present", transform),
                path,
                node,
            )];
        }
    }

    if let Some(path_check) = obj.get("pathCheck").and_then(|v| v.as_str()) {
        let current_path = path.join("/");
        if !current_path.starts_with(path_check) {
            return vec![err(
                "dynamicValidation",
                format!("Path '{}' does not match '{}'", current_path, path_check),
                path,
                node,
            )];
        }
    }

    vec![]
}

pub fn validate_cfn_lint(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let registry = match validator.cfn_lint_rules() {
        Some(r) => r,
        None => return vec![],
    };
    let keywords = match constraint.as_array() {
        Some(arr) => arr,
        None => return vec![],
    };
    let mut errors = Vec::new();
    let mut seen_kw = std::collections::HashSet::new();
    for kw in keywords {
        if let Some(kw_str) = kw.as_str() {
            if seen_kw.insert(kw_str.to_string()) {
                errors.extend(registry.dispatch(validator, kw_str, node, schema, path));
            }
        }
    }
    errors
}

pub fn validate_function_structure(
    validator: &Validator,
    fn_name: &str,
    args: &AstNode,
    path: &[String],
) -> Vec<ValidationError> {
    let schema = match FUNCTION_SCHEMAS.get(fn_name) {
        Some(s) => s,
        None => return vec![],
    };

    let v = Validator {
        validators: validator.validators.clone(),
        root_schema: schema.clone(),
        store: validator.store.clone(),
        strict_types: validator.strict_types,
        context: validator.context.clone(),
        cfn_lint_rules: None,
        cfn_path: vec![],
    };
    let errs = v.validate_schema(args, schema, path);
    errs.into_iter().filter(|e| !e.unknown).collect()
}
