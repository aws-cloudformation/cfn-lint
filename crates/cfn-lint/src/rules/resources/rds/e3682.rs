crate::extension_schema_rule!(
    E3682,
    id: "E3682",
    description: "Validate when using Aurora certain properties are not required",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/aurora_exclusive.json",
    regional: false
);
