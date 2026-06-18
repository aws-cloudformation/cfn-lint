crate::extension_schema_rule!(
    E3647,
    id: "E3647",
    description: "Validate ElastiCache cluster cache node type",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElastiCache::CacheCluster",
    schema_path: "../../../../data/schemas/extensions/aws_elasticache_cachecluster/cachenodetype_enum.json",
    regional: true,
    property: "CacheNodeType"
);
