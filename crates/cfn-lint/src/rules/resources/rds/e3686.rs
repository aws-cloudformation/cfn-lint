crate::extension_schema_rule!(
    E3686,
    id: "E3686",
    description: "Validate allowed properties when using a serverless RDS DB cluster",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/serverless_exclusive.json",
    regional: false
);
