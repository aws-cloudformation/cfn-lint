crate::extension_schema_rule!(
    W3693,
    id: "W3693",
    description: "Validate Aurora DB cluster configuration for ignored properties",
    severity: crate::rules::Severity::Warning,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/aurora_warning.json",
    regional: false
);
