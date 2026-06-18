use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E2530: SnapStart supports the configured runtime.
///
/// To properly leverage SnapStart, you must have a supported runtime.
pub struct E2530;

const INVALID_SNAPSTART_RUNTIMES: &[&str] = &[
    "dotnet5.0",
    "dotnet6",
    "dotnet7",
    "java8.al2",
    "java8",
    "python3.10",
    "python3.11",
    "python3.7",
    "python3.8",
    "python3.9",
];

fn is_runtime_valid_for_snapstart(runtime: &str) -> bool {
    if !runtime.starts_with("python")
        && !runtime.starts_with("java")
        && !runtime.starts_with("dotnet")
    {
        return false;
    }
    if runtime.starts_with("dotnetcore") {
        return false;
    }
    !INVALID_SNAPSTART_RUNTIMES.contains(&runtime)
}

impl CfnLintRule for E2530 {
    fn id(&self) -> &str {
        "E2530"
    }
    fn short_description(&self) -> &str {
        "SnapStart supports the configured runtime"
    }
    fn description(&self) -> &str {
        "To properly leverage SnapStart, you must have a supported runtime"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Lambda::Function/Properties"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let obj = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        // Check if SnapStart is configured with ApplyOn: PublishedVersions
        let snap_start = match obj.get("SnapStart").and_then(|s| s.as_object()) {
            Some(s) => s,
            None => return vec![],
        };

        let apply_on = match snap_start.get("ApplyOn").and_then(|a| a.as_str()) {
            Some(s) if s == "PublishedVersions" => s,
            _ => return vec![],
        };
        let _ = apply_on;

        // Validate the runtime
        let runtime = match obj.get("Runtime").and_then(|r| r.as_str()) {
            Some(r) => r,
            None => return vec![],
        };

        if !is_runtime_valid_for_snapstart(runtime) {
            let mut err_path = path.to_vec();
            err_path.push("SnapStart".to_string());
            err_path.push("ApplyOn".to_string());

            let span = snap_start
                .get("ApplyOn")
                .map(|n| n.span())
                .unwrap_or_default();

            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "{:?} is not supported for 'SnapStart' enabled functions",
                    runtime
                ),
                path: err_path,
                span,
                unknown: false,
                resolved_from_ref: false,
                context: vec![],
                schema_id: None,
            }];
        }

        vec![]
    }
}

crate::register_cfn_lint_rule!(E2530);
