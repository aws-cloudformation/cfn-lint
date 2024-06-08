"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.helpers import TRANSFORM_SAM
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class ServerlessTransform(CfnLintKeyword):
    """Check if Serverless Resources exist without the Serverless Transform"""

    id = "E3038"
    shortdesc = "Check if Serverless Resources have Serverless Transform"
    description = (
        "Check that a template with Serverless Resources also includes the Serverless"
        " Transform"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/transform-aws-serverless.html"
    tags = ["resources", "transform"]

    def __init__(self) -> None:
        super().__init__(keywords=["Resources/*/Type"])

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        if validator.context.transforms.has_sam_transform():
            return

        if instance.startswith("AWS::Serverless::"):
            yield ValidationError(
                (
                    f"{instance!r} type used without the "
                    f"serverless transform {TRANSFORM_SAM!r}"
                ),
                rule=self,
            )
