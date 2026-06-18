crate::extension_schema_rule!(
    E3641,
    id: "E3641",
    description: "Validate GameLift Fleet EC2 instance type",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::GameLift::Fleet",
    schema_path: "../../../../data/schemas/extensions/aws_gamelift_fleet/ec2instancetype_enum.json",
    regional: true,
    property: "EC2InstanceType"
);
