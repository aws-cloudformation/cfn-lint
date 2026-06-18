use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// W3011: Check resources with UpdateReplacePolicy/DeletionPolicy have both.
///
/// Both UpdateReplacePolicy and DeletionPolicy are needed to protect resources
/// from deletion. Having only one with a non-Delete value is flagged.
/// Excludes AWS::Lambda::Version and AWS::Lambda::LayerVersion.
pub struct W3011;

impl CfnLintRule for W3011 {
    fn id(&self) -> &str {
        "W3011"
    }
    fn short_description(&self) -> &str {
        "Check resources with UpdateReplacePolicy/DeletionPolicy have both"
    }
    fn description(&self) -> &str {
        "Both UpdateReplacePolicy and DeletionPolicy are needed to protect \
         resources from deletion"
    }
    fn severity(&self) -> Severity {
        Severity::Warning
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/*"]
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

        // Skip excluded resource types
        let resource_type = obj.get("Type").and_then(|t| t.as_str()).unwrap_or("");
        if EXCLUDED_TYPES.contains(&resource_type) {
            return vec![];
        }

        let deletion = obj.get("DeletionPolicy");
        let update = obj.get("UpdateReplacePolicy");

        let has_deletion = deletion.is_some();
        let has_update = update.is_some();

        // If both present or neither present, no issue
        if has_deletion == has_update {
            return vec![];
        }

        // One is present without the other - check if the present one is "Delete"
        let is_delete = if has_deletion {
            deletion.and_then(|n| n.as_str()) == Some("Delete")
        } else {
            update.and_then(|n| n.as_str()) == Some("Delete")
        };

        if is_delete {
            return vec![];
        }

        vec![ValidationError {
            rule_id: None,
            keyword: format!("cfnLint:{}", self.id()),
            message: "Both 'UpdateReplacePolicy' and 'DeletionPolicy' are needed \
                      to protect resource from deletion"
                .to_string(),
            path: path.to_vec(),
            span: instance.span(),
            unknown: false,
            resolved_from_ref: false,
            context: vec![],
            schema_id: None,
        }]
    }
}

const EXCLUDED_TYPES: &[&str] = &["AWS::Lambda::Version", "AWS::Lambda::LayerVersion"];

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_both_policies_set() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
    UpdateReplacePolicy: Retain
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("Bucket").unwrap();
        let path = vec!["Resources".to_string(), "Bucket".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3011.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_only_deletion_policy_retain() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Retain
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("Bucket").unwrap();
        let path = vec!["Resources".to_string(), "Bucket".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3011.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert_eq!(errors.len(), 1);
    }

    #[test]
    fn test_only_deletion_policy_delete_is_ok() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    DeletionPolicy: Delete
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("Bucket").unwrap();
        let path = vec!["Resources".to_string(), "Bucket".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3011.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_neither_policy() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("Bucket").unwrap();
        let path = vec!["Resources".to_string(), "Bucket".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3011.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }

    #[test]
    fn test_lambda_version_excluded() {
        let yaml = br#"
Resources:
  Ver:
    Type: AWS::Lambda::Version
    DeletionPolicy: Retain
    Properties:
      FunctionName: !Ref Func
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap().get("Ver").unwrap();
        let path = vec!["Resources".to_string(), "Ver".to_string()];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = W3011.validate(
            &validator,
            "Resources/*",
            instance,
            &serde_json::json!({}),
            &path,
        );
        assert!(errors.is_empty());
    }
}

crate::register_cfn_lint_rule!(W3011);
