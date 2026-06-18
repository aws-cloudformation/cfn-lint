crate::extension_schema_rule!(
    E3635,
    id: "E3635",
    description: "Validate Neptune DB instance class",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Neptune::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_neptune_dbinstance/dbinstanceclass_enum.json",
    regional: true,
    property: "DBInstanceClass"
);
