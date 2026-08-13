use std::collections::HashMap;

use crate::ast::AstNode;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;
use crate::jsonschema::ValidationError;
use crate::rules::Severity;
use crate::template::Template;

/// E2529: Check for SubscriptionFilters having beyond 2 attachments to a
/// CloudWatch Log Group.
///
/// The current limit for a CloudWatch Log Group is 2 subscription filters.
/// We look for duplicate LogGroupNames inside Subscription Filters (and SAM
/// CloudWatchLogs events) and make sure they are within 2.
pub struct E2529;

const SUBSCRIPTION_FILTER_LIMIT: usize = 2;

/// Serialize an AstNode to a string for comparison purposes.
/// Unlike Display, this includes all function arguments to distinguish
/// between e.g. !Ref LogGroup1 and !Ref LogGroup2.
fn serialize_node(node: &AstNode) -> String {
    match node {
        AstNode::String(s) => format!("\"{}\"", s.value),
        AstNode::Number(n) => format!("{}", n.value),
        AstNode::Bool(b) => format!("{}", b.value),
        AstNode::Null(_) => "null".to_string(),
        AstNode::Object(obj) => {
            let mut parts: Vec<String> = obj
                .iter()
                .map(|(k, v)| format!("{}:{}", k, serialize_node(v)))
                .collect();
            parts.sort(); // Ensure consistent ordering
            format!("{{{}}}", parts.join(","))
        }
        AstNode::Array(arr) => {
            let parts: Vec<String> = arr.elements.iter().map(serialize_node).collect();
            format!("[{}]", parts.join(","))
        }
        AstNode::Function(func) => {
            format!("{}({})", func.name, serialize_node(&func.args))
        }
    }
}

impl CfnLintRule for E2529 {
    fn id(&self) -> &str {
        "E2529"
    }
    fn short_description(&self) -> &str {
        "Check for SubscriptionFilters have beyond 2 attachments to a CloudWatch Log Group"
    }
    fn description(&self) -> &str {
        "The current limit for a CloudWatch Log Group is they can have 2 subscription \
         filters. We will look for duplicate LogGroupNames inside Subscription Filters \
         and SAM CloudWatchLogs events and make sure they are within 2."
    }
    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(
        &self,
        template: &Template,
        root: &AstNode,
    ) -> Vec<crate::jsonschema::ValidationError> {
        // Group subscription filter paths by their serialized LogGroupName
        // Value: (serialized_log_group_name, Vec<(path, span)>)
        let mut log_group_map: HashMap<String, Vec<(Vec<String>, crate::ast::Span)>> =
            HashMap::new();

        // Enumerate AWS::Logs::SubscriptionFilter resources
        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::Logs::SubscriptionFilter" {
                continue;
            }

            // Get from AST to properly serialize the node
            let log_group_name_node = root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"))
                .and_then(|p| p.get("LogGroupName"));

            let log_group_name = match log_group_name_node {
                Some(n) => serialize_node(n),
                None => continue,
            };

            let span = log_group_name_node.map(|n| n.span()).unwrap_or_default();

            let path = vec![
                "Resources".to_string(),
                name.clone(),
                "Properties".to_string(),
                "LogGroupName".to_string(),
            ];

            log_group_map
                .entry(log_group_name)
                .or_default()
                .push((path, span));
        }

        // Enumerate AWS::Serverless::Function CloudWatchLogs events
        for (name, resource) in &template.resources {
            if resource.resource_type != "AWS::Serverless::Function" {
                continue;
            }

            // Get the properties from the AST to examine Events
            let props_node = root
                .get("Resources")
                .and_then(|r| r.get(name))
                .and_then(|r| r.get("Properties"));

            let props_node = match props_node {
                Some(p) => p,
                None => continue,
            };

            let events = match props_node.get("Events") {
                Some(e) => e,
                None => continue,
            };

            let events_obj = match events.as_object() {
                Some(o) => o,
                None => continue,
            };

            for (event_id, event_node) in events_obj.iter() {
                let event_obj = match event_node.as_object() {
                    Some(o) => o,
                    None => continue,
                };

                // Check if this is a CloudWatchLogs event
                let event_type = event_obj.get("Type").and_then(|t| t.as_str());
                if event_type != Some("CloudWatchLogs") {
                    continue;
                }

                // Get the LogGroupName from Properties
                let event_props = match event_obj.get("Properties") {
                    Some(p) => p,
                    None => continue,
                };

                let log_group_name_node = match event_props.get("LogGroupName") {
                    Some(n) => n,
                    None => continue,
                };

                let log_group_name = serialize_node(log_group_name_node);
                let span = log_group_name_node.span();

                let path = vec![
                    "Resources".to_string(),
                    name.clone(),
                    "Properties".to_string(),
                    "Events".to_string(),
                    event_id.to_string(),
                    "Properties".to_string(),
                    "LogGroupName".to_string(),
                ];

                log_group_map
                    .entry(log_group_name)
                    .or_default()
                    .push((path, span));
            }
        }

        let mut issues = Vec::new();
        for paths in log_group_map.values() {
            if paths.len() > SUBSCRIPTION_FILTER_LIMIT {
                // Report on the third (index 2) occurrence which exceeds the limit
                if let Some((path, span)) = paths.get(SUBSCRIPTION_FILTER_LIMIT) {
                    issues.push(ValidationError {
                        rule_id: Some(self.id().to_string()),
                        message: format!(
                            "You can only have {} Subscription Filters per CloudWatch Log Group",
                            SUBSCRIPTION_FILTER_LIMIT
                        ),
                        path: path.clone(),
                        span: *span,
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

    #[test]
    fn test_sam_cloudwatchlogs_exceeds_limit() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/lambda/my-function
  LogSubscriptionFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello_world/
      Handler: app.lambda_handler
      Runtime: python3.9
      Events:
        Event1:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref MyLogGroup
            FilterPattern: ""
        Event2:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref MyLogGroup
            FilterPattern: ""
        Event3:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref MyLogGroup
            FilterPattern: ""
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E2529.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
        assert_eq!(issues[0].rule_id.as_deref(), Some("E2529"));
        // Verify path points to the SAM function's event
        assert_eq!(issues[0].path[0], "Resources");
        assert_eq!(issues[0].path[1], "LogSubscriptionFunction");
        assert_eq!(issues[0].path[3], "Events");
    }

    #[test]
    fn test_sam_cloudwatchlogs_within_limit() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/lambda/my-function
  LogSubscriptionFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello_world/
      Handler: app.lambda_handler
      Runtime: python3.9
      Events:
        Event1:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref MyLogGroup
            FilterPattern: ""
        Event2:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref MyLogGroup
            FilterPattern: ""
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E2529.validate_template(&tmpl, &ast);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_sam_cloudwatchlogs_unique_log_groups() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  LogGroup1:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/lambda/function1
  LogGroup2:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/lambda/function2
  LogGroup3:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/lambda/function3
  LogSubscriptionFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello_world/
      Handler: app.lambda_handler
      Runtime: python3.9
      Events:
        Event1:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref LogGroup1
            FilterPattern: ""
        Event2:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref LogGroup2
            FilterPattern: ""
        Event3:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref LogGroup3
            FilterPattern: ""
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E2529.validate_template(&tmpl, &ast);
        assert!(issues.is_empty());
    }

    #[test]
    fn test_mixed_subscription_filter_and_sam_events() {
        // 1 explicit SubscriptionFilter + 2 SAM events = 3 total, exceeds limit
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyLogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /aws/lambda/my-function
  ExplicitFilter:
    Type: AWS::Logs::SubscriptionFilter
    Properties:
      LogGroupName: !Ref MyLogGroup
      FilterPattern: ""
      DestinationArn: arn:aws:lambda:us-east-1:123456789012:function:f
  LogSubscriptionFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello_world/
      Handler: app.lambda_handler
      Runtime: python3.9
      Events:
        Event1:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref MyLogGroup
            FilterPattern: ""
        Event2:
          Type: CloudWatchLogs
          Properties:
            LogGroupName: !Ref MyLogGroup
            FilterPattern: ""
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E2529.validate_template(&tmpl, &ast);
        assert_eq!(issues.len(), 1);
    }

    #[test]
    fn test_sam_non_cloudwatchlogs_event_ignored() {
        let yaml = br#"
Transform: AWS::Serverless-2016-10-31
Resources:
  MyFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: hello_world/
      Handler: app.lambda_handler
      Runtime: python3.9
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /hello
            Method: get
        SqsEvent:
          Type: SQS
          Properties:
            Queue: !GetAtt MyQueue.Arn
  MyQueue:
    Type: AWS::SQS::Queue
"#;
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let issues = E2529.validate_template(&tmpl, &ast);
        assert!(issues.is_empty());
    }
}

crate::register_cfn_lint_rule!(E2529);
