use super::super::{ValidationError, Validator};
use super::functions::validate_function_structure;
use super::helpers::{compile_getatt_regex, err, unknown_err};
use crate::ast::AstNode;
use std::sync::Arc;

pub fn validate_fn_getatt(
    validator: &Validator,
    node: &AstNode,
    _constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let func = match node.as_function() {
        Some(f) => f,
        None => return vec![unknown_err("fn_getatt", path, node)],
    };
    let ctx = match &validator.context {
        Some(c) => c,
        None => return vec![unknown_err("fn_getatt", path, node)],
    };
    let (resource_name, attribute) = match func.args.as_ref() {
        AstNode::Array(arr) if arr.elements.len() == 2 => match arr.elements[0].as_str() {
            Some(r) => match arr.elements[1].as_str() {
                Some(a) => (r.to_string(), a.to_string()),
                None => {
                    if arr.elements[1].as_function().is_some()
                        || arr.elements[1].as_object().is_some()
                    {
                        let display = match arr.elements[1].as_function() {
                            Some(f) => format!("{{'{}':", f.name),
                            None => "object".to_string(),
                        };
                        return vec![err(
                            "fn_getatt",
                            format!("{} is not of type 'string'", display),
                            path,
                            node,
                        )];
                    }
                    return vec![unknown_err("fn_getatt", path, node)];
                }
            },
            None => return vec![unknown_err("fn_getatt", path, node)],
        },
        AstNode::String(s) => match s.value.split_once('.') {
            Some((r, a)) => (r.to_string(), a.to_string()),
            None => {
                return vec![err(
                    "fn_getatt",
                    "Fn::GetAtt must have resource.attribute format".to_string(),
                    path,
                    node,
                )]
            }
        },
        _ => return vec![unknown_err("fn_getatt", path, node)],
    };

    let resource = match ctx.template.resources.get(&resource_name) {
        Some(r) => r,
        None => {
            let mut names: Vec<&str> = ctx.template.resources.keys().map(|s| s.as_str()).collect();
            names.sort();
            return vec![err(
                "fn_getatt",
                format!("'{}' is not one of {:?}", resource_name, names),
                path,
                node,
            )];
        }
    };

    if !resource.valid_atts.is_empty() {
        let valid = resource.valid_atts.iter().any(|a| {
            if a == "*" || a == &attribute {
                return true;
            }
            if a.contains('(')
                || a.contains('[')
                || a.contains('.')
                || a.contains('*')
                || a.contains('+')
                || a.contains('?')
                || a.contains('{')
            {
                compile_getatt_regex(a)
                    .map(|re| re.is_match(&attribute))
                    .unwrap_or(false)
            } else {
                false
            }
        });
        if !valid {
            return vec![err(
                "fn_getatt",
                format!("'{}' is not one of {:?}", attribute, resource.valid_atts),
                path,
                node,
            )];
        }
    }

    vec![unknown_err("fn_getatt", path, node)]
}

pub fn validate_ref(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let func = match node {
        AstNode::Function(f) if f.name == "Ref" => f,
        _ => return vec![unknown_err("ref", path, node)],
    };

    let ref_name = match func.args.as_str() {
        Some(s) => s,
        None => {
            return vec![err(
                "ref",
                "Ref value must be a string".to_string(),
                path,
                node,
            )]
        }
    };

    if ref_name == "AWS::NoValue" {
        let at_properties_level = path.last().is_some_and(|p| p == "Properties");
        if !at_properties_level {
            return vec![];
        }
    }

    let ctx = match &validator.context {
        Some(c) => c,
        None => return vec![unknown_err("ref", path, node)],
    };

    // Extension schemas run in unresolvable_function_mode. We no longer special-case
    // Ref here: resolution is suppressed at the common chokepoint
    // `Context::resolve_ref`, which returns no scenarios in that mode. That makes the
    // `scenarios.is_empty()` branch below emit an unknown=true error (left unvalidated,
    // suppressed by the existing unknown filtering) — and crucially also covers every
    // other intrinsic (Fn::Sub, Fn::FindInMap, Fn::If, …) that resolves through the
    // same chokepoint, not just Ref.
    let mut e1020_errors = Vec::new();
    // In unresolvable_function_mode we suppress all parameter-derived findings,
    // including the E1020 array/string type check, so the value is left unvalidated.
    if !ctx.unresolvable_function_mode {
        if let Some(param) = ctx.template.parameters.get(ref_name) {
            if let Some(schema_type) = constraint.get("type").and_then(|t| t.as_str()) {
                let ref_returns_string = !param.param_type.starts_with("List<")
                    && param.param_type != "CommaDelimitedList"
                    && !param.param_type.starts_with("AWS::SSM::Parameter");
                if ref_returns_string && schema_type == "array" {
                    e1020_errors.push(err(
                        "E1020",
                        format!(
                            "{:?} is not of type '{}'",
                            serde_json::json!({"Ref": ref_name}),
                            schema_type
                        ),
                        path,
                        node,
                    ));
                }
            }
        }
    }

    let scenarios = ctx.resolve_ref(ref_name);
    if scenarios.is_empty() {
        return vec![unknown_err("ref", path, node)];
    }

    let is_param = ctx.template.parameters.contains_key(ref_name);
    let mut errors = Vec::new();

    for scenario in scenarios {
        let evolved = Validator {
            validators: validator.validators.clone(),
            root_schema: validator.root_schema.clone(),
            store: validator.store.clone(),
            strict_types: validator.strict_types,
            context: Some(Arc::new(scenario.context)),
            cfn_lint_rules: validator.cfn_lint_rules.clone(),
            cfn_path: validator.cfn_path.clone(),
        };

        let mut errs = evolved.validate_schema(&scenario.value, constraint, path);
        if is_param {
            for e in &mut errs {
                e.resolved_from_ref = true;
            }
        }
        errors.extend(errs);
    }
    errors.extend(e1020_errors);
    errors
}

pub fn validate_fn_if(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let func = match node {
        AstNode::Function(f) if f.name == "Fn::If" => f,
        _ => return vec![unknown_err("fn_if", path, node)],
    };

    let arr = match func.args.as_array() {
        Some(a) if a.elements.len() == 3 => a,
        _ => {
            return vec![err(
                "fn_if",
                "Fn::If requires [condition, true_value, false_value]".to_string(),
                path,
                node,
            )]
        }
    };

    let cond_name = match arr.elements[0].as_str() {
        Some(s) => s,
        None => {
            return vec![err(
                "fn_if",
                "Fn::If condition must be a string".to_string(),
                path,
                node,
            )]
        }
    };

    let ctx = match &validator.context {
        Some(c) => c,
        None => return vec![unknown_err("fn_if", path, node)],
    };

    let mut errors = Vec::new();
    let condition_undefined = !ctx.template.conditions.contains_key(cond_name);

    if condition_undefined {
        let mut names: Vec<&str> = ctx.template.conditions.keys().map(|s| s.as_str()).collect();
        names.sort();
        errors.push(err(
            "fn_if",
            format!("'{}' is not one of {:?}", cond_name, names),
            path,
            &arr.elements[0],
        ));
        // Don't return early — continue validating branches so nested Fn::If
        // conditions are also checked (matching Python's behavior).
        // Branch errors are marked unknown so only nested condition-reference
        // errors bubble up.
    }

    let scenarios = ctx.evaluate_condition(cond_name);

    for scenario in &scenarios {
        let branch = if scenario.value {
            &arr.elements[1]
        } else {
            &arr.elements[2]
        };

        if let AstNode::Function(f) = branch {
            if f.name == "Ref" {
                if let Some(n) = f.args.as_str() {
                    if n == "AWS::NoValue" {
                        continue;
                    }
                }
            }
        }

        let evolved = Validator {
            validators: validator.validators.clone(),
            root_schema: validator.root_schema.clone(),
            store: validator.store.clone(),
            strict_types: validator.strict_types,
            context: Some(Arc::new(scenario.context.clone())),
            cfn_lint_rules: validator.cfn_lint_rules.clone(),
            cfn_path: validator.cfn_path.clone(),
        };

        // The constraint is {"fn_if": <inner_schema>} — validate branch against
        // the inner schema so that maxItems, minItems, pattern etc. are checked.
        let inner_schema = constraint.get("fn_if").unwrap_or(constraint);
        let branch_errors = evolved.validate_schema(branch, inner_schema, path);
        if condition_undefined {
            // Condition doesn't exist — mark branch errors as unknown so only
            // nested condition-reference errors (fn_if) bubble up, not schema
            // validation errors on the branches themselves.
            for mut e in branch_errors {
                if e.keyword != "fn_if" {
                    e.unknown = true;
                }
                errors.push(e);
            }
        } else {
            errors.extend(branch_errors);
        }
    }

    if errors.is_empty() && scenarios.is_empty() {
        return vec![unknown_err("fn_if", path, node)];
    }
    errors
}

pub fn validate_fn_sub(
    validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let func = match node.as_function() {
        Some(f) => f,
        None => return vec![unknown_err("fn_sub", path, node)],
    };
    let ctx = match &validator.context {
        Some(c) => c,
        None => return vec![unknown_err("fn_sub", path, node)],
    };

    let structure_errs = validate_function_structure(validator, "Fn::Sub", &func.args, path);
    if !structure_errs.is_empty() {
        return structure_errs
            .into_iter()
            .map(|mut e| {
                e.keyword = "E1019".to_string();
                e
            })
            .collect();
    }

    let (tmpl_str, local_vars) = match func.args.as_ref() {
        AstNode::String(s) => (Some(s.value.as_str()), std::collections::HashSet::new()),
        AstNode::Array(arr) if arr.elements.len() == 2 => {
            let s = arr.elements[0].as_str();
            let vars: std::collections::HashSet<&str> = arr.elements[1]
                .as_object()
                .map(|o| o.keys().collect())
                .unwrap_or_default();
            let has_invalid_ref = arr.elements[1].as_object().is_some_and(|o| {
                let valid_refs_check: std::collections::HashSet<&str> = ctx
                    .template
                    .parameters
                    .keys()
                    .map(|s| s.as_str())
                    .chain(ctx.template.resources.keys().map(|s| s.as_str()))
                    .chain(
                        [
                            "AWS::AccountId",
                            "AWS::NoValue",
                            "AWS::NotificationARNs",
                            "AWS::Partition",
                            "AWS::Region",
                            "AWS::StackId",
                            "AWS::StackName",
                            "AWS::URLSuffix",
                        ]
                        .iter()
                        .copied(),
                    )
                    .collect();
                o.values().any(|v| {
                    if let Some(f) = v.as_function() {
                        if f.name == "Ref" {
                            if let Some(ref_val) = f.args.as_str() {
                                return !valid_refs_check.contains(ref_val);
                            }
                        }
                    }
                    false
                })
            });
            if has_invalid_ref {
                return vec![unknown_err("fn_sub", path, node)];
            }
            (s, vars)
        }
        _ => (None, std::collections::HashSet::new()),
    };

    if let Some(tmpl) = tmpl_str {
        let valid_refs: std::collections::HashSet<&str> = ctx
            .template
            .parameters
            .keys()
            .map(|s| s.as_str())
            .chain(ctx.template.resources.keys().map(|s| s.as_str()))
            .chain(
                [
                    "AWS::AccountId",
                    "AWS::NoValue",
                    "AWS::NotificationARNs",
                    "AWS::Partition",
                    "AWS::Region",
                    "AWS::StackId",
                    "AWS::StackName",
                    "AWS::URLSuffix",
                ]
                .iter()
                .copied(),
            )
            .collect();

        let mut var_errors = Vec::new();
        let bytes = tmpl.as_bytes();
        let mut i = 0;
        while i < bytes.len() {
            if i + 1 < bytes.len() && bytes[i] == b'$' && bytes[i + 1] == b'{' {
                if i + 2 < bytes.len() && bytes[i + 2] == b'!' {
                    i += 3;
                    while i < bytes.len() && bytes[i] != b'}' {
                        i += 1;
                    }
                    i += 1;
                    continue;
                }
                let start = i + 2;
                let mut end = start;
                while end < bytes.len() && bytes[end] != b'}' {
                    end += 1;
                }
                let var = tmpl[start..end].trim();
                if !var.is_empty() {
                    if var.contains('.') {
                        let resource_name = var.split('.').next().unwrap_or("");
                        if !resource_name.is_empty()
                            && !valid_refs.contains(resource_name)
                            && !local_vars.contains(resource_name)
                        {
                            let mut all: Vec<&str> = valid_refs
                                .iter()
                                .chain(local_vars.iter())
                                .copied()
                                .collect();
                            all.sort();
                            var_errors.push(err(
                                "fn_sub",
                                format!("'{}' is not one of {:?}", resource_name, all),
                                path,
                                node,
                            ));
                        }
                    } else if !valid_refs.contains(var) && !local_vars.contains(var) {
                        let mut all: Vec<&str> = valid_refs
                            .iter()
                            .chain(local_vars.iter())
                            .copied()
                            .collect();
                        all.sort();
                        var_errors.push(err(
                            "fn_sub",
                            format!("'{}' is not one of {:?}", var, all),
                            path,
                            node,
                        ));
                    }
                }
                i = end + 1;
            } else {
                i += 1;
            }
        }
        if !var_errors.is_empty() {
            return var_errors;
        }
    }

    let resolver = crate::resolver::Resolver::new(ctx);
    let original_span = node.span();
    match resolver.resolve(node) {
        Some(resolved) => {
            let errs = validator.validate_schema(&resolved, constraint, path);
            errs.into_iter()
                .map(|mut e| {
                    super::fn_resolve::relabel_resolved(&mut e, "W1031", "Fn::Sub");
                    e.span = original_span;
                    e
                })
                .collect()
        }
        None => vec![unknown_err("fn_sub", path, node)],
    }
}
