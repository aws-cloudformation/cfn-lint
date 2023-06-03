"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class CacheClusterCacheNodeTypeEnum(BaseCfnRegionSchema):
    id = "E3647"
    shortdesc = "Validate ElastiCache cluster cache node type"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = "aws_elasticache_cachecluster/cachenodetype_enum"
