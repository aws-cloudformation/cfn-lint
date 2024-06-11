"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbcluster
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DbClusterInstanceClassEnum(CfnLintJsonSchemaRegional):
    id = "E3694"
    shortdesc = "Validates RDS DB Cluster instance class"
    description = (
        "Validates the RDS DB Cluster instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBCluster/Properties"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.extensions.aws_rds_dbcluster,
                "dbclusterinstanceclass_enum.json",
            ),
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        # RDS pricing schemas are based on values
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=[],
            )
        )

        yield from super().validate(validator, keywords, instance, schema)
