crate::extension_schema_rule!(
    E3690,
    id: "E3690",
    description: "Validate DB Cluster Engine and Engine Version",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/engine_version.json",
    regional: false
);
