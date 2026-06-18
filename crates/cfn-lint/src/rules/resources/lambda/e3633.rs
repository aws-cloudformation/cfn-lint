crate::extension_schema_rule!(
    E3633,
    id: "E3633",
    description: "Validate Lambda event source mapping StartingPosition is used correctly",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Lambda::EventSourceMapping",
    schema_path: "../../../../data/schemas/extensions/aws_lambda_eventsourcemapping/eventsourcearn_stream_inclusive.json",
    regional: false
);
