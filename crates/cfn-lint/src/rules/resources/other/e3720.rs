crate::extension_schema_rule!(
    E3720,
    id: "E3720",
    description: "Validate StorageEncrypted is set when KmsKeyId is specified",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/kmskey_storageencrypted.json",
    regional: false
);
