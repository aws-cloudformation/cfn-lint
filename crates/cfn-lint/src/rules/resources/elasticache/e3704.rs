crate::extension_schema_rule!(
    E3704,
    id: "E3704",
    description: "TransitEncryptionEnabled required for Valkey engine",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::ElastiCache::ReplicationGroup",
    schema_path: "../../../../data/schemas/extensions/aws_elasticache_replicationgroup/transitencryptionenabled_valkey.json",
    regional: false
);
