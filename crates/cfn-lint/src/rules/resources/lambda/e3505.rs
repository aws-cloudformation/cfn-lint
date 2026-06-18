crate::extension_schema_rule!(
    E3505,
    id: "E3505",
    description: "Validate SQS VisibilityTimeout is greater than Lambda function Timeout",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Lambda::EventSourceMapping",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_eventsourcemapping/event_source_sqs_timeout.json",
    regional: false
);
