crate::extension_schema_rule!(
    E3692,
    id: "E3692",
    description: "Validate Multi-AZ DB cluster configuration",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/multiaz.json",
    regional: false
);
