use crate::ast::AstNode;
use crate::jsonschema::{ValidationError, Validator};

fn best_match(errs: Vec<ValidationError>) -> Option<ValidationError> {
    if errs.is_empty() {
        return None;
    }
    errs.into_iter().max_by_key(|e| e.path.len())
}

/// Standalone validation function for extension schema rules (non-regional).
/// With `all_matches=true`: yields all errors with original messages.
/// With `all_matches=false`: picks best match, replaces message with short_desc.
pub fn validate_schema(
    id: &str,
    short_desc: &str,
    validator: &Validator,
    instance: &AstNode,
    schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    validate_schema_matches(id, short_desc, validator, instance, schema, path, true)
}

pub fn validate_schema_best_match(
    id: &str,
    short_desc: &str,
    validator: &Validator,
    instance: &AstNode,
    schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    validate_schema_matches(id, short_desc, validator, instance, schema, path, false)
}

fn validate_schema_matches(
    id: &str,
    short_desc: &str,
    validator: &Validator,
    instance: &AstNode,
    schema: &serde_json::Value,
    path: &[String],
    all_matches: bool,
) -> Vec<ValidationError> {
    let v = Validator {
        validators: validator.validators.clone(),
        root_schema: schema.clone(),
        store: validator.store.clone(),
        strict_types: validator.strict_types,
        context: validator.context.clone(),
        cfn_lint_rules: None,
        cfn_path: vec![],
    };
    let errs = v.validate_schema(instance, schema, path);
    let real_errs: Vec<_> = errs.into_iter().filter(|e| !e.unknown).collect();

    if !all_matches {
        if let Some(best) = best_match(real_errs) {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", id),
                message: short_desc.to_string(),
                path: best.path,
                span: best.span,
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }
        return vec![];
    }

    // all_matches=true: yield every error with its original message
    let mut results = Vec::new();
    for e in real_errs {
        if !e.context.is_empty() {
            for ctx_err in &e.context {
                if !ctx_err.unknown {
                    results.push(ValidationError {
                        rule_id: Some(id.to_string()),
                        keyword: format!("cfnLint:{}", id),
                        message: ctx_err.message.clone(),
                        path: ctx_err.path.clone(),
                        span: ctx_err.span.clone(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }
        } else {
            results.push(ValidationError {
                rule_id: Some(id.to_string()),
                keyword: format!("cfnLint:{}", id),
                message: e.message,
                path: e.path,
                span: e.span,
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }
    }
    results
}

/// Standalone validation function for regional extension schema rules.
/// The schema JSON is an object keyed by region name; each region's sub-schema
/// is validated independently.
pub fn validate_regional(
    id: &str,
    short_desc: &str,
    validator: &Validator,
    instance: &AstNode,
    schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let regions = match validator.context() {
        Some(ctx) => ctx.regions.clone(),
        None => return vec![],
    };
    let mut errors = Vec::new();
    for region in &regions {
        let region_schema = schema
            .get(region.as_str())
            .unwrap_or(&serde_json::Value::Bool(true));
        if region_schema == &serde_json::Value::Bool(true) {
            continue;
        }
        let v = validator.without_cfn_lint_rules();
        let errs = v.validate_schema(instance, region_schema, path);
        let real_errs: Vec<_> = errs.into_iter().filter(|e| !e.unknown).collect();

        if let Some(best) = best_match(real_errs) {
            errors.push(ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", id),
                message: format!("{} in {:?}", short_desc, region),
                path: best.path,
                span: best.span,
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            });
        }
    }
    errors
}
