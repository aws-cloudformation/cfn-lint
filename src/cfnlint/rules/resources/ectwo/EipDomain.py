"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

_valid_domains = {"standard", "vpc"}


class EipDomain(CfnLintKeyword):
    id = "W3700"
    shortdesc = "Non-standard Domain values are converted to vpc"
    description = (
        "When Domain is specified with a value other than 'standard' or 'vpc', "
        "the value is silently converted to 'vpc'. Use 'vpc' explicitly "
        "to avoid confusion."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-eip.html"
    tags = ["resources", "ec2"]

    def __init__(self) -> None:
        super().__init__(
            [
                "Resources/AWS::EC2::EIP/Properties/Domain",
            ]
        )

    def validate(
        self, validator: Validator, _: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not isinstance(instance, str):
            return

        if instance.lower() not in _valid_domains:
            yield ValidationError(
                f"{instance!r} is not a standard Domain value. "
                "Non-standard values are silently converted to 'vpc'."
            )
