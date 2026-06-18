crate::extension_schema_rule!(
    W3691,
    id: "W3691",
    description: "Validate DB Instance Engine Version is not deprecated",
    severity: crate::rules::Severity::Warning,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/engine_version_deprecated.json",
    regional: false
);
