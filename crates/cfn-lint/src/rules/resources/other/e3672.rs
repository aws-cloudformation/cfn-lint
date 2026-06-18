crate::extension_schema_rule!(
    E3672,
    id: "E3672",
    description: "Validate the cluster node type for a DAX Cluster",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::DAX::Cluster",
    schema_path: "../../../../data/schemas/extensions/aws_dax_cluster/nodetype_enum.json",
    regional: true,
    property: "NodeType"
);
