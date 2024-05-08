"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_dynamodb_table
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class TableBillingModeProvisioned(CfnLintJsonSchema):
    id = "E3639"
    shortdesc = "When BillingMode is Provisioned you must specify ProvisionedThroughput"
    description = (
        "When 'BillingMode' is 'Provisioned' 'ProvisionedThroughput' is required"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::DynamoDB::Table/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_dynamodb_table,
                filename="billingmode_provisioned_dependent.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "'ProvisionedThroughput' is a required property"
