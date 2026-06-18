crate::extension_schema_rule!(
    E3691,
    id: "E3691",
    description: "Validate DB Instance Engine and Engine Version",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/engine_version.json",
    regional: false
);
