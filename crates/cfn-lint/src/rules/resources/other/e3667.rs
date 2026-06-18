crate::extension_schema_rule!(
    E3667,
    id: "E3667",
    description: "Validate RedShift cluster node type",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Redshift::Cluster",
    schema_path: "../../../../data/schemas/extensions/aws_redshift_cluster/nodetype_enum.json",
    regional: true,
    property: "NodeType"
);
