use super::super::{ValidationError, Validator};
use super::helpers::err;
use crate::ast::AstNode;

/// Format a numeric bound for an error message. Integer-valued bounds are
/// rendered without a fractional part (e.g. `5`), while genuinely fractional
/// bounds are shown as-is (e.g. `1.5`). Casting to `i64` unconditionally would
/// wrongly report `minimum: 1.5` as "minimum of 1".
fn format_bound(bound: f64) -> String {
    if bound.fract() == 0.0 && bound.is_finite() {
        format!("{}", bound as i64)
    } else {
        format!("{}", bound)
    }
}

pub fn validate_minimum(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let min = match constraint
        .as_f64()
        .or_else(|| constraint.as_str().and_then(|s| s.parse::<f64>().ok()))
    {
        Some(m) => m,
        None => return vec![],
    };
    let val = node
        .as_f64()
        .or_else(|| node.as_str().and_then(|s| s.parse::<f64>().ok()));
    if let Some(val) = val {
        if val.is_finite() && val < min {
            let display = node
                .as_str()
                .map(|s| format!("'{}'", s))
                .unwrap_or_else(|| format!("{}", val));
            return vec![err(
                "minimum",
                format!(
                    "{} is less than the minimum of {}",
                    display,
                    format_bound(min)
                ),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_maximum(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let max = match constraint
        .as_f64()
        .or_else(|| constraint.as_str().and_then(|s| s.parse::<f64>().ok()))
    {
        Some(m) => m,
        None => return vec![],
    };
    // Try number first, then parse string as number (matches Python behavior)
    let val = node
        .as_f64()
        .or_else(|| node.as_str().and_then(|s| s.parse::<f64>().ok()));
    if let Some(val) = val {
        if val.is_finite() && val > max {
            let display = node
                .as_str()
                .map(|s| format!("'{}'", s))
                .unwrap_or_else(|| format!("{}", val));
            return vec![err(
                "maximum",
                format!(
                    "{} is greater than the maximum of {}",
                    display,
                    format_bound(max)
                ),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_exclusive_minimum(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let min = constraint
        .as_f64()
        .or_else(|| constraint.as_str().and_then(|s| s.parse::<f64>().ok()));
    let val = node
        .as_f64()
        .or_else(|| node.as_str().and_then(|s| s.parse::<f64>().ok()));
    if let (Some(val), Some(min)) = (val, min) {
        if val <= min {
            return vec![err(
                "exclusiveMinimum",
                format!("{} is not greater than {}", val, min),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_exclusive_maximum(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    let max = constraint
        .as_f64()
        .or_else(|| constraint.as_str().and_then(|s| s.parse::<f64>().ok()));
    let val = node
        .as_f64()
        .or_else(|| node.as_str().and_then(|s| s.parse::<f64>().ok()));
    if let (Some(val), Some(max)) = (val, max) {
        if val >= max {
            return vec![err(
                "exclusiveMaximum",
                format!("{} is not less than {}", val, max),
                path,
                node,
            )];
        }
    }
    vec![]
}

pub fn validate_multiple_of(
    _validator: &Validator,
    node: &AstNode,
    constraint: &serde_json::Value,
    _schema: &serde_json::Value,
    path: &[String],
) -> Vec<ValidationError> {
    if let (Some(val), Some(divisor)) = (node.as_f64(), constraint.as_f64()) {
        if divisor != 0.0 {
            let quotient = val / divisor;
            if (quotient - quotient.round()).abs() > 1e-9 {
                return vec![err(
                    "multipleOf",
                    format!("{} is not a multiple of {}", val, divisor),
                    path,
                    node,
                )];
            }
        }
    }
    vec![]
}
