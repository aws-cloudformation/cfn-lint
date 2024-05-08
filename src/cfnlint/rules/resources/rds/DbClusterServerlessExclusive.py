"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbcluster
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbClusterServerlessExclusive(CfnLintJsonSchema):
    id = "E3686"
    shortdesc = (
        "Validate when using a serverless RDS DB certain properties aren't needed"
    )
    description = (
        "When creating a serverless 'EngineMode' don't specify 'ScalingConfiguration'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBCluster/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbcluster,
                filename="serverless_exclusive.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "Additional properties are not allowed ('ScalingConfiguration')"
