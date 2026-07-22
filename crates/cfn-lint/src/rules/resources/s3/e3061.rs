use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::{ValidationError, Validator};
use crate::rules::Severity;

/// E3061: Validate the days for tierings in IntelligentTieringConfigurations.
///
/// ARCHIVE_ACCESS: 90-730 days, DEEP_ARCHIVE_ACCESS: 180-730 days.
pub struct E3061;

impl CfnLintRule for E3061 {
    fn id(&self) -> &str {
        "E3061"
    }
    fn short_description(&self) -> &str {
        "Validate the days for tierings in IntelligentTieringConfigurations"
    }
    fn description(&self) -> &str {
        "When using S3 IntelligentTieringConfigurations the Tierings have minimum and maximum values"
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["Resources/AWS::S3::Bucket/Properties/IntelligentTieringConfigurations/*/Tierings/*"]
    }

    fn validate(
        &self,
        _validator: &Validator,
        _keyword: &str,
        instance: &AstNode,
        _schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        let access_tier = match instance.get("AccessTier").and_then(|a| a.as_str()) {
            Some(s) => s.to_string(),
            None => return vec![],
        };

        let limits = match tiering_limits(&access_tier) {
            Some(l) => l,
            None => return vec![],
        };

        let days_node = match instance.get("Days") {
            Some(n) => n,
            None => return vec![],
        };

        let days = days_node
            .as_f64()
            .map(|n| n as i64)
            .or_else(|| days_node.as_str().and_then(|s| s.parse().ok()));

        if let Some(days) = days {
            if days < limits.min || days > limits.max {
                let mut days_path = path.to_vec();
                days_path.push("Days".to_string());
                return vec![ValidationError {
                    rule_id: None,
                    keyword: format!("cfnLint:{}", self.id()),
                    message: format!(
                        "Days {} for {} must be between {} and {}",
                        days, access_tier, limits.min, limits.max
                    ),
                    path: days_path,
                    span: days_node.span(),
                    unknown: false,
                    resolved_from_ref: false,
                    context: vec![],
                    schema_id: None,
                }];
            }
        }

        vec![]
    }
}

struct TieringLimits {
    min: i64,
    max: i64,
}

fn tiering_limits(access_tier: &str) -> Option<TieringLimits> {
    match access_tier {
        "ARCHIVE_ACCESS" => Some(TieringLimits { min: 90, max: 730 }),
        "DEEP_ARCHIVE_ACCESS" => Some(TieringLimits { min: 180, max: 730 }),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;

    #[test]
    fn test_stubbed_out() {
        let yaml = br#"
Resources:
  Bucket:
    Type: AWS::S3::Bucket
    Properties:
      IntelligentTieringConfigurations:
        - Id: config1
          Tierings:
            - AccessTier: ARCHIVE_ACCESS
              Days: 30
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3061.validate_template(&tmpl, &ast).is_empty());
    }
}

crate::register_cfn_lint_rule!(E3061);
