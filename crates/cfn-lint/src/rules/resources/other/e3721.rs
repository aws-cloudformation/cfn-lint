crate::extension_schema_rule!(
    E3721,
    id: "E3721",
    description: "Validate ReplicaMode value for Oracle and Db2 engines",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBInstance",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbinstance/replicamode_enum.json",
    regional: false
);
