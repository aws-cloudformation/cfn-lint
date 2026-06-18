crate::extension_schema_rule!(
    E3628,
    id: "E3628",
    description: "Validate EC2 instance types based on region",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::EC2::Instance",
    schema_path: "../../../../data/schemas/extensions/aws_ec2_instance/instancetype_enum.json",
    regional: true,
    property: "InstanceType"
);
