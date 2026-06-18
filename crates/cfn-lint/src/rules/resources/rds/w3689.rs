crate::extension_schema_rule!(
    W3689,
    id: "W3689",
    description: "When using a source DB certain properties are ignored",
    severity: crate::rules::Severity::Warning,
    resource_type: "AWS::RDS::DBCluster",
    schema_path: "../../../../data/schemas/extensions/aws_rds_dbcluster/sourcedbclusteridentifier.json",
    regional: false
);
