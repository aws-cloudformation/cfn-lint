"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class FunctionLayerArnLength(CfnLintKeyword):
    id = "E3716"
    shortdesc = "Validate Lambda layer ARN length based on region"
    description = (
        "Validates the Lambda layer ARN length based on region. "
        "Max length is 176 + len(partition) + len(region)."
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/chapter-layers.html"
    tags = ["resources", "lambda"]

    def __init__(self) -> None:
        super().__init__(["Resources/AWS::Lambda::Function/Properties/Layers/*"])

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, str):
            return

        for region in validator.context.regions:
            partition = self._get_partition(region)
            max_length = 176 + len(partition) + len(region)
            if len(instance) > max_length:
                yield ValidationError(
                    f"{instance!r} is longer than {max_length} in {region!r}"
                )

    @staticmethod
    def _get_partition(region: str) -> str:
        if region.startswith("cn-"):
            return "aws-cn"
        if region.startswith("us-gov-"):
            return "aws-us-gov"
        if region.startswith("us-iso-") or region.startswith("us-isof-"):
            return "aws-iso"
        if region.startswith("us-isob-"):
            return "aws-iso-b"
        if region.startswith("eu-isoe-"):
            return "aws-iso-e"
        if region.startswith("eusc-"):
            return "aws-iso-f"
        return "aws"
