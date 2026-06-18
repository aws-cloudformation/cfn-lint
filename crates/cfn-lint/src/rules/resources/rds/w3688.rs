crate::extension_schema_rule!(
    W3688,
    id: "W3688",
    description: "When restoring DBCluster certain properties are ignored",
    severity: crate::rules::Severity::Warning,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/snapshotidentifier.json",
    regional: false
);
