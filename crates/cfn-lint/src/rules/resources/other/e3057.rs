use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3057: Validate that CloudFront TargetOriginId is a specified Origin.
///
/// CloudFront TargetOriginId has to map to an Origin Id that is in the same
/// DistributionConfig.
pub struct E3057;

impl CfnLintRule for E3057 {
    fn id(&self) -> &str { "E3057" }
    fn short_description(&self) -> &str {
        "Validate that CloudFront TargetOriginId is a specified Origin"
    }
    fn description(&self) -> &str {
        "CloudFront TargetOriginId has to map to an Origin Id that is in the same DistributionConfig"
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let dist_config = match instance.as_object() {
            Some(o) => o,
            None => return vec![],
        };

        // Collect origin IDs
        let origin_ids: Vec<&str> = dist_config
            .get("Origins")
            .and_then(|o| o.as_array())
            .map(|arr| {
                arr.elements
                    .iter()
                    .filter_map(|e| e.get("Id").and_then(|id| id.as_str()))
                    .collect()
            })
            .unwrap_or_default();

        let mut errors = Vec::new();

        // Check DefaultCacheBehavior TargetOriginId
        if let Some(target_id_node) = dist_config
            .get("DefaultCacheBehavior")
            .and_then(|dcb| dcb.get("TargetOriginId"))
        {
            if let Some(target_id) = target_id_node.as_str() {
                if !origin_ids.contains(&target_id) {
                    let mut err_path = path.to_vec();
                    err_path.push("DefaultCacheBehavior".to_string());
                    err_path.push("TargetOriginId".to_string());
                    errors.push(ValidationError {
                rule_id: None,
                        keyword: format!("cfnLint:{}", self.id()),
                        message: format!(
                            "'{}' is not one of {:?}",
                            target_id, origin_ids
                        ),
                        path: err_path,
                        span: target_id_node.span(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }
        }

        errors
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_valid_target_origin_id() {
        let yaml = br#"
Resources:
  Dist:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: myS3Origin
            DomainName: mybucket.s3.amazonaws.com
        DefaultCacheBehavior:
          TargetOriginId: myS3Origin
          ViewerProtocolPolicy: allow-all
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Dist").unwrap()
            .get("Properties").unwrap()
            .get("DistributionConfig").unwrap();
        let path = vec![
            "Resources".to_string(), "Dist".to_string(),
            "Properties".to_string(), "DistributionConfig".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3057.validate(&validator, "Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig", instance, &serde_json::json!({}), &path);
        assert!(errors.is_empty());
    }

    #[test]
    fn test_invalid_target_origin_id() {
        let yaml = br#"
Resources:
  Dist:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - Id: myS3Origin
            DomainName: mybucket.s3.amazonaws.com
        DefaultCacheBehavior:
          TargetOriginId: nonExistentOrigin
          ViewerProtocolPolicy: allow-all
"#;
        let ast = parser::parse(yaml).unwrap();
        let instance = ast.get("Resources").unwrap()
            .get("Dist").unwrap()
            .get("Properties").unwrap()
            .get("DistributionConfig").unwrap();
        let path = vec![
            "Resources".to_string(), "Dist".to_string(),
            "Properties".to_string(), "DistributionConfig".to_string(),
        ];
        let validator = crate::jsonschema::Validator::new(serde_json::json!({}));
        let errors = E3057.validate(&validator, "Resources/AWS::CloudFront::Distribution/Properties/DistributionConfig", instance, &serde_json::json!({}), &path);
        assert_eq!(errors.len(), 1);
        assert!(errors[0].message.contains("nonExistentOrigin"));
    }
}

crate::register_cfn_lint_rule!(E3057);
