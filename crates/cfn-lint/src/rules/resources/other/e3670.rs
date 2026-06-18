crate::extension_schema_rule!(
    E3670,
    id: "E3670",
    description: "Validate the instance types for an AmazonMQ Broker",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::AmazonMQ::Broker",
    schema_path: "../../../../data/schemas/extensions/aws_amazonmq_broker/instancetype_enum.json",
    regional: true,
    property: "HostInstanceType"
);
