crate::extension_schema_rule!(
    E3694,
    id: "E3694",
    description: "Validates RDS DB Cluster instance class",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/dbclusterinstanceclass_enum.json",
    regional: true
);
