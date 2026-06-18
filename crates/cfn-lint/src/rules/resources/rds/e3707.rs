crate::extension_schema_rule!(
    E3707,
    id: "E3707",
    description: "RDS DBInstance Engine must match DBCluster Engine",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/instance_cluster_engine.json",
    regional: false
);
