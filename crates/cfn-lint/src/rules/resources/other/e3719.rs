crate::extension_schema_rule!(
    E3719,
    id: "E3719",
    description: "Validate RDS BackupRetentionPeriod configuration",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/backupretentionperiod_maximum.json",
    regional: false
);
