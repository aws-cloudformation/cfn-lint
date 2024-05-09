"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_dynamodb_table
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class TableSseSpecification(CfnLintJsonSchema):
    id = "E3640"
    shortdesc = (
        "Validate DynamoDB SSE Specification has required properties when using KMS"
    )
    description = (
        "When doing KMS encryption in an AWS DynamoDB "
        "table there are required properties."
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::DynamoDB::Table/Properties/SSESpecification"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_dynamodb_table,
                filename="ssespecification_kms.json",
            ),
            all_matches=True,
        )
