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
    shortdesc = "Validate allowed properties when using a serverless RDS DB cluster"
    description = (
        "Validate that when EngineMode is 'serverless' or 'provisioned' that the "
        "appropriate allowed properties are provided. If 'EngineMode' is not provided "
        "make sure serverless properties don't exist at all."
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

        # validator None means the schema is falsy
        if err.validator is None:
            if instance.get("EngineMode") in ["serverless", "provisioned"]:
                return (
                    f"EngineMode {instance.get('EngineMode')!r} "
                    f" doesn't allow additional properties {err.path[0]!r}"
                )
            else:
                return "Additional properties are not allowed " f"({err.path[0]!r})"

        return err.message
