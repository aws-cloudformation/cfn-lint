crate::extension_schema_rule!(
    E3502,
    id: "E3502",
    description: "Validate SQS DLQ queues are the same type",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::SQS::Queue",
    schema_path: "../../../../data/schemas/extensions/aws_sqs_queue/queue_dlq.json",
    regional: false
);
