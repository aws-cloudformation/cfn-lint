crate::extension_schema_rule!(
    E3501,
    id: "E3501",
    description: "Extension schema validation",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::SQS::Queue",
    schema_path: "../../../../data/schemas/extensions/aws_sqs_queue/properties.json",
    regional: false
);
