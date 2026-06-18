crate::extension_schema_rule!(
    E3634,
    id: "E3634",
    description: "Validate Lambda event source mapping starting position is used with SQS",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Lambda::EventSourceMapping",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_eventsourcemapping/eventsourcearn_sqs_exclusive.json",
    regional: false
);
