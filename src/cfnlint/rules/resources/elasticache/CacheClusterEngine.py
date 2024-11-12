"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_elasticache_cachecluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class CacheClusterEngine(CfnLintJsonSchema):
    id = "E3695"
    shortdesc = "Validate Elasticache Cluster Engine and Engine Version"
    description = (
        "Validate the Elasticache cluster engine along with the engine version"
    )
    tags = ["resources"]
    source_url = "https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/supported-engine-versions.html"

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ElastiCache::CacheCluster/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticache_cachecluster,
                filename="engine_version.json",
            ),
            all_matches=True,
        )
