"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbcluster
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbClusterSourceDBClusterIdentifier(CfnLintJsonSchema):
    id = "W3689"
    shortdesc = "When using a source DB certain properties are ignored"
    description = (
        "When creating a DBCluster from a source certain properties "
        "are ignored and could result in drift"
    )
    tags = ["resources", "rds"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBCluster/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbcluster,
                filename="sourcedbclusteridentifier.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "Additional properties are ignored ('MasterUsername', "
            "'MasterUserPassword', 'StorageEncrypted')"
        )
