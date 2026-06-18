crate::extension_schema_rule!(
    W3690,
    id: "W3690",
    description: "Validate DB Cluster Engine Version is not deprecated",
    severity: crate::rules::Severity::Warning,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/engine_version_deprecated.json",
    regional: false
);
