use std::collections::HashMap;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;

/// E2529: Check for SubscriptionFilters having beyond 2 attachments to a
/// CloudWatch Log Group.
///
/// The current limit for a CloudWatch Log Group is 2 subscription filters.
/// We look for duplicate LogGroupNames inside Subscription Filters and make
/// sure they are within 2.
pub struct E2529;

const SUBSCRIPTION_FILTER_LIMIT: usize = 2;

impl CfnLintRule for E2529 {
    fn id(&self) -> &str { "E2529" }
    fn short_description(&self) -> &str {
        "Check for SubscriptionFilters have beyond 2 attachments to a CloudWatch Log Group"
    }
    fn description(&self) -> &str {
        "The current limit for a CloudWatch Log Group is they can have 2 subscription \
         filters. We will look for duplicate LogGroupNames inside Subscription Filters \
         and make sure they are within 2."
    }
    fn severity(&self) -> Severity { Severity::Error }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Group subscription filter resource names by their serialized LogGroupName
        let mut log_group_map: HashMap<String, Vec<String>> = HashMap::new();

        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::Logs::SubscriptionFilter" {
                continue;
            }
            let log_group_name = resource.properties.as_ref()
                .and_then(|p| p.get("LogGroupName"))
                .map(|n| format!("{}", n))
                .unwrap_or_default();

            log_group_map.entry(log_group_name).or_default().push(name.clone());
        }

        let mut issues = Vec::new();
        for (_, resources) in &log_group_map {
            if resources.len() > SUBSCRIPTION_FILTER_LIMIT {
                if let Some(res_name) = resources.get(SUBSCRIPTION_FILTER_LIMIT) {
                    let pos = template.resources.get(res_name)
                        .and_then(|r| r.properties.as_ref())
                        .map(|p| p.span().clone())
                        .unwrap_or_default();
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!(
                            "You can only have {} Subscription Filters per CloudWatch Log Group",
                            SUBSCRIPTION_FILTER_LIMIT
                        ),
                        path: vec!["Resources".to_string(), res_name.clone()],
                        span: pos,
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
});
                }
            }
        }
        issues
    }
}


#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_within_limit() {
        let yaml = br#"
Resources:
  Filter1:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      LogGroupName: /aws/lambda/my-function
      FilterPattern: ""
      DestinationArn: arn:aws:logs:us-east-1:123456789012:destination:my-dest
  Filter2:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      LogGroupName: /aws/lambda/my-function
      FilterPattern: ""
      DestinationArn: arn:aws:logs:us-east-1:123456789012:destination:my-dest2
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E2529.validate_template(&tmpl, &ast).is_empty());
    }

    #[test]
    fn test_exceeds_limit() {
        let yaml = br#"
Resources:
  Filter1:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      LogGroupName: /aws/lambda/my-function
      FilterPattern: ""
      DestinationArn: arn:aws:logs:us-east-1:123456789012:destination:d1
  Filter2:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      LogGroupName: /aws/lambda/my-function
      FilterPattern: ""
      DestinationArn: arn:aws:logs:us-east-1:123456789012:destination:d2
  Filter3:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      LogGroupName: /aws/lambda/my-function
      FilterPattern: ""
      DestinationArn: arn:aws:logs:us-east-1:123456789012:destination:d3
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E2529.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E2529"));
        assert!(issues[0].message.contains("2 Subscription Filters"));
    }
}

crate::register_cfn_lint_rule!(E2529);
