crate::extension_schema_rule!(
    E3025,
    id: "E3025",
    description: "Validates RDS DB Instance Class",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/dbinstanceclass_enum.json",
    regional: true
);
