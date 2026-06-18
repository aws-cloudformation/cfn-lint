use std::collections::HashMap;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E2531: Validate if lambda runtime is deprecated for creation.
///
/// Check if the lambda runtime has reached the create-block date but not
/// yet the update-block date.
pub struct E2531 {
    runtimes: HashMap<String, RuntimeData>,
}

#[derive(serde::Deserialize)]
struct RuntimeData {
    deprecated: Option<String>,
    #[serde(rename = "create-block")]
    create_block: Option<String>,
    #[serde(rename = "update-block")]
    update_block: Option<String>,
    successor: Option<String>,
}

fn today_str() -> String {
    let now = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs();
    let days = now / 86400;
    let mut y = 1970i64;
    let mut remaining = days as i64;
    loop {
        let days_in_year = if y % 4 == 0 && (y % 100 != 0 || y % 400 == 0) {
            366
        } else {
            365
        };
        if remaining < days_in_year {
            break;
        }
        remaining -= days_in_year;
        y += 1;
    }
    let leap = y % 4 == 0 && (y % 100 != 0 || y % 400 == 0);
    let month_days = [
        31,
        if leap { 29 } else { 28 },
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ];
    let mut m = 0;
    for (i, &d) in month_days.iter().enumerate() {
        if remaining < d as i64 {
            m = i + 1;
            break;
        }
        remaining -= d as i64;
    }
    format!("{:04}-{:02}-{:02}", y, m, remaining + 1)
}

impl Default for E2531 {
    fn default() -> Self {
        Self::new()
    }
}

impl E2531 {
    pub fn new() -> Self {
        let data = include_str!("../../../data/additional_specs/LmbdRuntimeLifecycle.json");
        let runtimes: HashMap<String, RuntimeData> = serde_json::from_str(data).unwrap_or_default();
        E2531 { runtimes }
    }
}

impl CfnLintRule for E2531 {
    fn id(&self) -> &str {
        "E2531"
    }
    fn short_description(&self) -> &str {
        "Validate if lambda runtime is deprecated"
    }
    fn description(&self) -> &str {
        "Check the lambda runtime has reached the end of life for creation"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &[
            "Resources/AWS::Lambda::Function/Properties/Runtime",
            "Resources/AWS::Serverless::Function/Properties/Runtime",
            "Globals/Function/Runtime",
        ]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let runtime = match instance.as_str() {
            Some(s) => s,
            None => return vec![],
        };

        let data = match self.runtimes.get(runtime) {
            Some(d) => d,
            None => return vec![],
        };

        let today = today_str();

        let create_block = match &data.create_block {
            Some(cb) => cb.as_str(),
            None => return vec![],
        };
        let update_block = match &data.update_block {
            Some(ub) => ub.as_str(),
            None => return vec![],
        };

        // Create blocked but update not yet blocked
        if create_block <= today.as_str() && update_block > today.as_str() {
            let successor = data.successor.as_deref().unwrap_or("a newer runtime");
            let deprecated = data.deprecated.as_deref().unwrap_or("unknown");
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "Runtime {:?} was deprecated on {:?}. Creation was disabled on {:?} \
                     and update on {:?}. Please consider updating to {:?}",
                    runtime, deprecated, create_block, update_block, successor
                ),
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
