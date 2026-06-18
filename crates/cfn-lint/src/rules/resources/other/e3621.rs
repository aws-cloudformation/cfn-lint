crate::extension_schema_rule!(
    E3621,
    id: "E3621",
    description: "Validate the instance types for AppStream Fleet",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::AppStream::Fleet",
    schema_path: "../../../../data/schemas/extensions/aws_appstream_fleet/instancetype_enum.json",
    regional: true,
    property: "InstanceType"
);
