crate::extension_schema_rule!(
    E3617,
    id: "E3617",
    description: "Validate ManagedBlockchain instance type",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ManagedBlockchain::Node",
    schema_path: "../../../../data/schemas/extensions/aws_managedblockchain_node/nodeconfiguration_instancetype_enum.json",
    regional: true,
    property: "NodeConfiguration/InstanceType"
);
