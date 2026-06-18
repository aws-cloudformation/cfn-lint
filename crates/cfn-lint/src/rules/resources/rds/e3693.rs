crate::extension_schema_rule!(
    E3693,
    id: "E3693",
    description: "Validate Aurora DB cluster configuration",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/aurora.json",
    regional: false
);
