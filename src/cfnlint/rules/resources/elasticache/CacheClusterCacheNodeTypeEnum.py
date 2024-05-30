"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_elasticache_cachecluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class CacheClusterCacheNodeTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3647"
    shortdesc = "Validate ElastiCache cluster cache node type"
    description = (
        "Validates the ElastiCache instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ElastiCache::CacheCluster/Properties/CacheNodeType"
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticache_cachecluster,
                filename="cachenodetype_enum.json",
            ),
        )
