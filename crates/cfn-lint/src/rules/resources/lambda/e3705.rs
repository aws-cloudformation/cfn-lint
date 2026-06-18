crate::extension_schema_rule!(
    E3705,
    id: "E3705",
    description: "SQS FIFO EventSourceMapping BatchSize max 10",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Lambda::EventSourceMapping",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_eventsourcemapping/event_source_sqs_fifo_batch_size.json",
    regional: false
);
