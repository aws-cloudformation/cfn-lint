crate::extension_schema_rule!(
    E3652,
    id: "E3652",
    description: "Validate Elasticsearch domain cluster instance type",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Elasticsearch::Domain",
    schema_path: "../../../../data/schemas/extensions/aws_elasticsearch_domain/elasticsearchclusterconfig_instancetype_enum.json",
    regional: true,
    property: "ElasticsearchClusterConfig/InstanceType"
);
