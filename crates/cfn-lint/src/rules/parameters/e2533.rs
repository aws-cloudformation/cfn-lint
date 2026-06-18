use std::collections::HashMap;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;
use crate::template::Template;

/// E2533: Check if Lambda Function Runtimes are updatable.
///
/// Check if an EOL Lambda Runtime is specified and you cannot update the function.
pub struct E2533 {
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

impl Default for E2533 {
    fn default() -> Self { Self::new() }
}

impl E2533 {
    pub fn new() -> Self {
        let data = include_str!("../../../data/additional_specs/LmbdRuntimeLifecycle.json");
        let runtimes: HashMap<String, RuntimeData> = serde_json::from_str(data).unwrap_or_default();
        E2533 { runtimes }
    }
}

impl CfnLintRule for E2533 {
    fn id(&self) -> &str { "E2533" }
    fn short_description(&self) -> &str { "Check if Lambda Function Runtimes are updatable" }
    fn description(&self) -> &str {
        "Check if an EOL Lambda Runtime is specified and you cannot update the function"
    }
    fn severity(&self) -> Severity { Severity::Error }

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

        let update_block = match &data.update_block {
            Some(ub) => ub.as_str(),
            None => return vec![],
        };

        // Update blocked
        if update_block <= today.as_str() {
            let successor = data.successor.as_deref().unwrap_or("a newer runtime");
            let deprecated = data.deprecated.as_deref().unwrap_or("unknown");
            let create_block = data.create_block.as_deref().unwrap_or("unknown");
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
    fn validate_template(&self, _template: &Template, root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        let runtime_node = root.get("Globals")
            .and_then(|g| g.get("Function"))
            .and_then(|f| f.get("Runtime"));

        let runtime = match runtime_node.and_then(|n| n.as_str()) {
            Some(s) => s,
            None => return vec![],
        };

        let data = match self.runtimes.get(runtime) {
            Some(d) => d,
            None => return vec![],
        };

        let today = today_str();

        let update_block = match &data.update_block {
            Some(ub) => ub.as_str(),
            None => return vec![],
        };

        if update_block <= today.as_str() {
            let successor = data.successor.as_deref().unwrap_or("a newer runtime");
            let deprecated = data.deprecated.as_deref().unwrap_or("unknown");
            let create_block = data.create_block.as_deref().unwrap_or("unknown");
            return vec![ValidationError {
                rule_id: Some(self.id().to_string()),
                message: format!(
                    "Runtime {:?} was deprecated on {:?}. Creation was disabled on {:?} \
                     and update on {:?}. Please consider updating to {:?}",
                    runtime, deprecated, create_block, update_block, successor
                ),
                path: vec!["Globals".to_string(), "Function".to_string(), "Runtime".to_string()],
                span: runtime_node.unwrap().span(),
                keyword: String::new(),
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }

}

