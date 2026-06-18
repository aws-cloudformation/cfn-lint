use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W2531: Check if EOL Lambda Function Runtimes are used.
pub struct W2531 {
    runtimes: serde_json::Value,
}

impl W2531 {
    pub fn new() -> Self {
        let data = include_str!("../../../data/additional_specs/LmbdRuntimeLifecycle.json");
        let runtimes: serde_json::Value = serde_json::from_str(data).unwrap_or_default();
        W2531 { runtimes }
    }

    fn today() -> String {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
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
        for (i, &md) in month_days.iter().enumerate() {
            if remaining < md as i64 {
                m = i + 1;
                break;
            }
            remaining -= md as i64;
        }
        format!("{:04}-{:02}-{:02}", y, m, remaining + 1)
    }
}

impl CfnLintRule for W2531 {
    fn id(&self) -> &str {
        "W2531"
    }
    fn short_description(&self) -> &str {
        "Check if EOL Lambda Function Runtimes are used"
    }
    fn description(&self) -> &str {
        "Check if an EOL Lambda Runtime is specified and give a warning if used"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Lambda::Function/Properties/Runtime"]
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
            Some(r) => r,
            None => return vec![],
        };

        let rt_data = match self.runtimes.get(runtime) {
            Some(d) => d,
            None => return vec![],
        };

        let now = Self::today();
        let deprecated = rt_data
            .get("deprecated")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let create_block = rt_data
            .get("create-block")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let update_block = rt_data
            .get("update-block")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        let successor = rt_data
            .get("successor")
            .and_then(|v| v.as_str())
            .unwrap_or("unknown");

        // Warn only if deprecated but not yet fully blocked
        if deprecated <= now.as_str() && create_block > now.as_str() && update_block > now.as_str()
        {
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "Runtime '{}' was deprecated on '{}'. Creation was disabled on '{}' \
                     and update on '{}'. Please consider updating to '{}'",
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_current_runtime_ok() {
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python3.12
      Handler: index.handler
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("Runtime")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "Runtime".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2531::new().validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties/Runtime",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_ancient_runtime_no_warn_past_block() {
        // python2.7 has create-block and update-block both in the past
        let yaml = br#"
Resources:
  Func:
    Type: AWS::Lambda::Function
    Properties:
      Runtime: python2.7
      Handler: index.handler
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Func")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("Runtime")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Func".to_string(),
            "Properties".to_string(),
            "Runtime".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W2531::new().validate(
            &validator,
            "Resources/AWS::Lambda::Function/Properties/Runtime",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }
}
