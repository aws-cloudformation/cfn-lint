crate::extension_schema_rule!(
    E3709,
    id: "E3709",
    description: "RDS DBInstance StorageEncrypted must match DBCluster",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/instance_cluster_storage_encrypted.json",
    regional: false
);
