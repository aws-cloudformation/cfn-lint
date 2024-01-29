"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class TableBillingModeExclusive(CfnLintJsonSchema):
    id = "E3638"
    shortdesc = "Validate DynamoDB BillingMode pay per request configuration"
    description = (
        "When 'BillingMode' is 'PAY_PER_REQUEST' don't specify 'ProvisionedThroughput'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(keywords=["aws_dynamodb_table/billingmode_exclusive"])
