crate::extension_schema_rule!(
    E3653,
    id: "E3653",
    description: "Validate OpenSearch domain cluster instance type",
    severity: crate::rules::Severity::Error,
    schema_path: "../../../../data/schemas/extensions/aws_opensearchservice_domain/clusterconfig_instancetype_enum.json",
    keywords: [
        "Resources/AWS::OpenSearchService::Domain/Properties/ClusterConfig/InstanceType",
    ]
);
