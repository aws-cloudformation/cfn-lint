use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3504: Backup plan lifecycle must have >= 90 days between cold and delete.
///
/// When a Backup plan lifecycle has both MoveToColdStorageAfterDays and
/// DeleteAfterDays, the delete value must be at least 90 days greater.
pub struct E3504;

impl CfnLintRule for E3504 {
    fn id(&self) -> &str {
        "E3504"
    }
    fn short_description(&self) -> &str {
        "Check minimum 90 period is met between BackupPlan cold and delete"
    }
    fn description(&self) -> &str {
        "Check that Backup plans with lifecycle rules have >= 90 days between cold and delete"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::Backup::BackupPlan/Properties/BackupPlan/BackupPlanRule/*/Lifecycle"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let lifecycle = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        let delete = match lifecycle.get("DeleteAfterDays").and_then(|n| n.as_f64()) {
            Some(v) => v,
            None => return vec![],
        };
        let cold = match lifecycle
            .get("MoveToColdStorageAfterDays")
            .and_then(|n| n.as_f64())
        {
            Some(v) => v,
            None => return vec![],
        };

        if delete - cold < 90.0 {
            let mut err_path = path.to_vec();
            err_path.push("DeleteAfterDays".to_string());
            return vec![ValidationError {
                rule_id: None,
                keyword: format!("cfnLint:{}", self.id()),
                message: format!(
                    "DeleteAfterDays {} must be at least 90 days after MoveToColdStorageAfterDays {}",
                    delete as i64, cold as i64
                ),
                path: err_path,
                span: lifecycle.get("DeleteAfterDays").map(|n| n.span()).unwrap_or_default(),
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
    fn test_valid_lifecycle() {
        let yaml = br#"
Resources:
  Plan:
    Type: AWS::Backup::BackupPlan
    Properties:
      BackupPlan:
        BackupPlanName: test
        BackupPlanRule:
          - RuleName: rule1
            TargetBackupVault: vault
            Lifecycle:
              MoveToColdStorageAfterDays: 10
              DeleteAfterDays: 100
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Plan")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("BackupPlan")
            .unwrap()
            .get("BackupPlanRule")
            .unwrap()
            .as_array()
            .unwrap()
            .elements
            .first()
            .unwrap()
            .get("Lifecycle")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Plan".to_string(),
            "Properties".to_string(),
            "BackupPlan".to_string(),
            "BackupPlanRule".to_string(),
            "0".to_string(),
            "Lifecycle".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3504.validate(
            &validator,
            "Resources/AWS::Backup::BackupPlan/Properties/BackupPlan/BackupPlanRule/*/Lifecycle",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_invalid_lifecycle() {
        let yaml = br#"
Resources:
  Plan:
    Type: AWS::Backup::BackupPlan
    Properties:
      BackupPlan:
        BackupPlanName: test
        BackupPlanRule:
          - RuleName: rule1
            TargetBackupVault: vault
            Lifecycle:
              MoveToColdStorageAfterDays: 10
              DeleteAfterDays: 50
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast
            .get("Resources")
            .unwrap()
            .get("Plan")
            .unwrap()
            .get("Properties")
            .unwrap()
            .get("BackupPlan")
            .unwrap()
            .get("BackupPlanRule")
            .unwrap()
            .as_array()
            .unwrap()
            .elements
            .first()
            .unwrap()
            .get("Lifecycle")
            .unwrap();
        let path = vec![
            "Resources".to_string(),
            "Plan".to_string(),
            "Properties".to_string(),
            "BackupPlan".to_string(),
            "BackupPlanRule".to_string(),
            "0".to_string(),
            "Lifecycle".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3504.validate(
            &validator,
            "Resources/AWS::Backup::BackupPlan/Properties/BackupPlan/BackupPlanRule/*/Lifecycle",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("90 days"));
    }
}

crate::register_cfn_lint_rule!(E3504);
