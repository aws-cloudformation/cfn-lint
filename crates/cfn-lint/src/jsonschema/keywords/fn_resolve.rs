use super::super::{ValidationError, Validator};
use super::functions::validate_function_structure;
use super::helpers::{err, unknown_err};
use crate::ast::AstNode;

pub fn validate_fn_resolvable(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let func = match node.as_function() {
        Some(f) => f,
        None => return vec![unknown_err("function", path, node)],
    };
    let ctx = match &validator.context {
        Some(c) => c,
        None => return vec![unknown_err("function", path, node)],
    };

    let fn_name = func.name.as_str();

    // Check if the function's return type is incompatible with the destination schema.
    if let Some(required_type) = constraint.get("type").and_then(|t| t.as_str()) {
        let possible_types = function_return_types(fn_name);
        if !possible_types.is_empty() && !possible_types.contains(&required_type) {
            let rule_id = match fn_name {
                "Fn::Sub" => "E1019",
                "Fn::Join" => "E1022",
                "Fn::Select" => "E1017",
                "Fn::Split" => "E1018",
                _ => "E1001",
            };
            return vec![ValidationError {
                keyword: rule_id.to_string(),
                message: format!("{{'{}'}} is not of type '{}'", fn_name, required_type),
                path: path.to_vec(),
                span: node.span(),
                ..Default::default()
            }];
        }
    }

    let structure_errs = validate_function_structure(validator, fn_name, &func.args, path);
    if !structure_errs.is_empty() {
        let rule_id = match fn_name {
            "Fn::Sub" => "E1019",
            "Fn::Join" => "E1022",
            "Fn::Select" => "E1017",
            "Fn::Split" => "E1018",
            _ => "E1001",
        };
        return structure_errs
            .into_iter()
            .map(|mut e| {
                e.keyword = rule_id.to_string();
                e
            })
            .collect();
    }

    let resolved_rule = match fn_name {
        "Fn::Join" => "W1032",
        _ => "",
    };

    if resolved_rule.is_empty() {
        return vec![unknown_err("function", path, node)];
    }

    let resolved = super::super::resolvers::resolve_value(ctx, node);
    if resolved.is_empty() {
        return vec![unknown_err("function", path, node)];
    }

    let original_span = node.span();
    let effective_constraint = inject_cfn_lint(validator, constraint, path);
    let mut errors = Vec::new();
    for r in &resolved {
        let errs = validator.validate_schema(&r.value, &effective_constraint, path);
        if errs.is_empty() {
            return vec![];
        }
        for mut e in errs {
            relabel_resolved(&mut e, resolved_rule, &func.name);
            e.span = original_span;
            errors.push(e);
        }
    }
    errors
}

fn inject_cfn_lint(
    validator: &Validator,
    constraint: &serde_json::Value,
    path: &[String],
) -> serde_json::Value {
    if validator.cfn_lint_rules.is_none() || validator.cfn_path.is_empty() {
        return constraint.clone();
    }
    let base_len = validator.cfn_path.len();
    let mut cfn_path_parts = validator.cfn_path.clone();
    if path.len() > base_len {
        cfn_path_parts.extend_from_slice(&path[base_len..]);
    }
    let cfn_path_str = cfn_path_parts.join("/");
    let mut modified = constraint.clone();
    if let Some(obj) = modified.as_object_mut() {
        let paths = obj
            .entry("cfnLint")
            .or_insert_with(|| serde_json::json!([]));
        if let Some(arr) = paths.as_array_mut() {
            arr.push(serde_json::Value::String(cfn_path_str));
        }
    }
    modified
}

pub fn validate_fn_resolve_and_check(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let func = match node.as_function() {
        Some(f) => f,
        None => return vec![unknown_err("function", path, node)],
    };
    let ctx = match &validator.context {
        Some(_c) => _c,
        None => return vec![unknown_err("function", path, node)],
    };

    let fn_name = func.name.as_str();

    let rule_id = match fn_name {
        "Fn::Base64" => "E1021",
        "Fn::Cidr" => "E1024",
        "Fn::FindInMap" => "E1011",
        "Fn::GetAZs" => "E1015",
        "Fn::ImportValue" => "E1016",
        "Fn::Length" => "E1030",
        "Fn::Select" => "E1017",
        "Fn::ToJsonString" => "E1031",
        _ => "E1001",
    };

    let structure_errs = validate_function_structure(validator, fn_name, &func.args, path);
    if !structure_errs.is_empty() {
        return structure_errs
            .into_iter()
            .map(|mut e| {
                e.keyword = rule_id.to_string();
                e
            })
            .collect();
    }

    // Check if the function's return type is incompatible with the destination schema.
    // This fires regardless of whether we can resolve the concrete value.
    if let Some(required_type) = constraint.get("type").and_then(|t| t.as_str()) {
        let possible_types = function_return_types(fn_name);
        if !possible_types.is_empty() && !possible_types.contains(&required_type) {
            return vec![ValidationError {
                keyword: rule_id.to_string(),
                message: format!("{{'{}'}} is not of type '{}'", fn_name, required_type),
                path: path.to_vec(),
                span: node.span(),
                ..Default::default()
            }];
        }
    }

    let resolved_rule = match fn_name {
        "Fn::GetAZs" => "W1036",
        "Fn::FindInMap" => "W1034",
        "Fn::Base64" => "E1021",
        "Fn::Select" => "W1035",
        _ => "",
    };

    let resolved = super::super::resolvers::resolve_value(ctx, node);
    if resolved.is_empty() {
        return vec![unknown_err("function", path, node)];
    }

    if resolved_rule.is_empty() {
        return vec![];
    }

    let original_span = node.span();
    let mut errors = Vec::new();
    for r in &resolved {
        let errs = validator.validate_schema(&r.value, constraint, path);
        if errs.is_empty() {
            return vec![];
        }
        for mut e in errs {
            e.span = original_span;
            if !resolved_rule.is_empty() {
                let effective_rule = if fn_name == "Fn::FindInMap" && e.keyword == "type" {
                    rule_id
                } else {
                    resolved_rule
                };
                relabel_resolved(&mut e, effective_rule, fn_name);
            }
            errors.push(e);
        }
    }
    errors
}

/// Return types a function can produce. Empty means "any type possible" (no constraint).
fn function_return_types(fn_name: &str) -> &'static [&'static str] {
    match fn_name {
        "Fn::Base64" => &["string"],
        "Fn::Cidr" => &["array"],
        "Fn::FindInMap" => &["array", "boolean", "integer", "number", "string"],
        "Fn::GetAtt" => &[], // all types
        "Fn::GetAZs" => &["array"],
        "Fn::GetStackOutput" => &["boolean", "integer", "number", "string"],
        "Fn::If" => &[], // all types
        "Fn::ImportValue" => &["boolean", "integer", "number", "string"],
        "Fn::Join" => &["string"],
        "Fn::Length" => &["integer"],
        "Fn::Select" => &[], // all types
        "Fn::Split" => &["array"],
        "Fn::Sub" => &["string"],
        "Fn::ToJsonString" => &["string"],
        "Ref" => &[], // all types
        _ => &[],
    }
}

pub fn relabel_resolved(err: &mut ValidationError, rule_id: &str, fn_name: &str) {
    err.keyword = rule_id.to_string();
    if !err.message.contains("is resolved") {
        err.message = format!("{} when '{}' is resolved", err.message, fn_name);
    }
    for ctx_err in &mut err.context {
        relabel_resolved(ctx_err, rule_id, fn_name);
    }
}
