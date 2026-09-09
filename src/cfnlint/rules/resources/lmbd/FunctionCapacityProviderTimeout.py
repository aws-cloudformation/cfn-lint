"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FunctionCapacityProviderTimeout(CfnLintJsonSchema):
    id = "E3717"
    shortdesc = "Validate Lambda function Timeout based on CapacityProviderConfig"
    description = (
        "The maximum Timeout of 900 seconds only applies to functions without "
        "CapacityProviderConfig. Functions using Lambda Managed Instances "
        "(CapacityProviderConfig) can specify a Timeout up to 5400 seconds."
    )
    source_url = (
        "https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html"
    )
    tags = ["resources", "lambda"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Lambda::Function/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="capacity_provider_timeout.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        timeout = instance.get("Timeout")
        return (
            f"{timeout} is greater than the maximum of 900 for functions "
            "without 'CapacityProviderConfig' (Lambda Managed Instances)"
        )
