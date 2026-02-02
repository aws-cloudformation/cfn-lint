"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_elasticache_replicationgroup
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class ReplicationGroupValkeyTransitEncryption(CfnLintJsonSchema):
    id = "E3704"
    shortdesc = "Validate TransitEncryptionEnabled is set when using Valkey engine"
    description = (
        "When Engine is valkey, TransitEncryptionEnabled must be explicitly set"
    )
    tags = ["resources", "elasticache"]
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticache-replicationgroup.html#cfn-elasticache-replicationgroup-transitencryptionenabled"

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::ElastiCache::ReplicationGroup/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticache_replicationgroup,
                filename="transitencryptionenabled_valkey.json",
            ),
            all_matches=True,
        )
