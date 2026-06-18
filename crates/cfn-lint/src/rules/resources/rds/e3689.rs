crate::extension_schema_rule!(
    E3689,
    id: "E3689",
    description: "Validate MonitoringInterval and MonitoringRoleArn are used together",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/monitoring.json",
    regional: false
);
