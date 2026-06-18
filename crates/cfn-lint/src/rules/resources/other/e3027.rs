use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

pub struct E3027;

impl CfnLintRule for E3027 {
    fn id(&self) -> &str {
        "E3027"
    }
    fn short_description(&self) -> &str {
        "Validate AWS Event ScheduleExpression format"
    }
    fn description(&self) -> &str {
        "Validates EventBridge/CloudWatch Events schedule expressions"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Events::Rule/Properties/ScheduleExpression"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let val = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        if let Some(msg) = validate_schedule(val) {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: msg,
                path: path.to_vec(),
                span: instance.span(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

fn validate_schedule(val: &str) -> Option<String> {
    if let Some(inner) = val.strip_prefix("rate(").and_then(|s| s.strip_suffix(')')) {
        return validate_rate(inner);
    }
    if let Some(inner) = val.strip_prefix("cron(").and_then(|s| s.strip_suffix(')')) {
        return validate_cron(inner);
    }
    Some(format!("{:?} has to be either 'cron()' or 'rate()'", val))
}

fn validate_rate(inner: &str) -> Option<String> {
    if inner.is_empty() {
        return Some("rate expression cannot be empty".to_string());
    }

    let parts: Vec<&str> = inner.split_whitespace().collect();
    if parts.len() != 2 {
        return Some(format!("{:?} has to be of format rate(Value Unit)", inner));
    }

    let n: u64 = match parts[0].parse() {
        Ok(v) => v,
        Err(_) => {
            return Some(format!("{:?} is not of type 'integer'", parts[0]));
        }
    };

    if n == 0 {
        return Some(format!("{:?} is less than the minimum of 0", parts[0]));
    }

    let valid_periods = if n <= 1 {
        &["minute", "hour", "day"][..]
    } else {
        &["minutes", "hours", "days"][..]
    };

    if !valid_periods.contains(&parts[1]) {
        return Some(format!("{:?} is not one of {:?}", parts[1], valid_periods));
    }

    None
}

fn validate_cron(inner: &str) -> Option<String> {
    if inner.is_empty() {
        return Some("cron expression cannot be empty".to_string());
    }

    let fields: Vec<&str> = inner.split_whitespace().collect();
    if fields.len() != 6 {
        return Some(format!(
            "Cron expression must have exactly 6 fields \
             (Minutes Hours Day-of-month Month Day-of-week Year), got {}",
            fields.len()
        ));
    }

    // Day-of-month and Day-of-week cannot both be specified
    let day_of_month = fields[2];
    let day_of_week = fields[4];
    if day_of_month != "?" && day_of_week != "?" {
        return Some(
            "Cron expression cannot specify both Day-of-month and Day-of-week. \
             One must be '?'"
                .to_string(),
        );
    }

    None
}

crate::register_cfn_lint_rule!(E3027);
