"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class LambdaFunctionAwsLayer(CfnLintJsonSchema):
    id = "W3702"
    shortdesc = "awslayer ARN format may not be available"
    description = "Layer ARNs using the 'awslayer' format may not be available."
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html"
    tags = ["resources", "lambda"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Lambda::Function/Properties/Layers/*",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="awslayer.json",
            ),
            all_matches=False,
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return f"{instance!r} uses the 'awslayer' format which may not be available"
