crate::extension_schema_rule!(
    E3620,
    id: "E3620",
    description: "Validate a DocDB DB Instance class",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::DocDB::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_docdb_dbinstance/dbinstanceclass_enum.json",
    regional: true,
    property: "DBInstanceClass"
);
