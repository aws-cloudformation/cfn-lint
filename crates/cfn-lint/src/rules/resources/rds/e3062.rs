crate::extension_schema_rule!(
    E3062,
    id: "E3062",
    description: "Validates RDS DB Instance Class based on Engine and EngineVersion",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/db_instance_class.json",
    regional: false
);
