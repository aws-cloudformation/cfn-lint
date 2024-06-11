"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DbInstanceDbInstanceClassEnum(CfnLintJsonSchemaRegional):
    id = "E3025"
    shortdesc = "Validates RDS DB Instance Class"
    description = (
        "Validates the RDS DB instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBInstance/Properties"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                "dbinstanceclass_enum.json",
            ),
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        validator = validator.evolve(
            context=validator.context.evolve(
                functions=[],
            )
        )

        if validator.is_type(instance.get("Engine"), "string"):
            instance["Engine"] = instance["Engine"].lower()

        yield from super().validate(validator, keywords, instance, schema)
