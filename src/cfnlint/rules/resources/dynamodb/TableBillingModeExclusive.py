"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_dynamodb_table
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class TableBillingModeExclusive(CfnLintJsonSchema):
    id = "E3638"
    shortdesc = "Validate DynamoDB BillingMode pay per request configuration"
    description = (
        "When 'BillingMode' is 'PAY_PER_REQUEST' don't specify 'ProvisionedThroughput'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::DynamoDB::Table/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_dynamodb_table,
                filename="billingmode_exclusive.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "Additional properties are not allowed ('ProvisionedThroughput')"
