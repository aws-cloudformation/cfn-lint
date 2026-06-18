crate::extension_schema_rule!(
    E3695,
    id: "E3695",
    description: "Validate Elasticache Cluster Engine and Engine Version",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElastiCache::CacheCluster",
    schema_path: "../../../../data/schemas/extensions/aws_elasticache_cachecluster/engine_version.json",
    regional: false
);
