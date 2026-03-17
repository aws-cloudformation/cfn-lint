"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceClusterStorageEncrypted(CfnLintJsonSchema):
    id = "E3709"
    shortdesc = "Validate RDS DBInstance StorageEncrypted matches DBCluster"
    description = (
        "When a DBInstance references a DBCluster via DBClusterIdentifier, "
        "the StorageEncrypted property must match between the two resources"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbinstance.html"
    tags = ["resources", "rds"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::RDS::DBInstance/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="instance_cluster_storage_encrypted.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
