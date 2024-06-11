"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class SnapStart(CfnLintKeyword):
    """Check if Lambda SnapStart is properly configured"""

    id = "W2530"
    shortdesc = "Validate that SnapStart is properly configured"
    description = (
        "To properly leverage SnapStart, you must configure both the lambda function "
        "and attach a Lambda version resource"
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html"
    tags = ["resources", "lambda"]

    def __init__(self):
        super().__init__(
            ["Resources/AWS::Lambda::Function/Properties/SnapStart/ApplyOn"]
        )

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        if instance != "PublishedVersions":
            return

        resource_name: str = str(validator.context.path.path[1])
        lambda_version_type = "AWS::Lambda::Version"
        if list(
            validator.cfn.get_resource_children(resource_name, [lambda_version_type])
        ):
            return

        yield ValidationError(
            (
                f"'SnapStart' is enabled but an {lambda_version_type!r} "
                "resource is not attached"
            ),
        )
