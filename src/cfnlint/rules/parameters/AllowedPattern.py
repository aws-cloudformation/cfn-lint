"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import regex as re

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class AllowedPattern(CfnLintKeyword):

    id = "I2003"
    shortdesc = "Validate AllowedPattern is a valid regexs"
    description = (
        "Validate the pattern defined in a AllowedPattern. "
        "This is informational as the service side regex library is "
        "different than the Python one"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["parameters", "allowed pattern"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Parameters/*/AllowedPattern",
            ]
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        if not validator.is_type(instance, "string"):
            return

        try:
            re.compile(instance)
        except Exception as e:
            yield ValidationError(
                f"{instance!r} could not be compiled ({str(e)})", rule=self
            )
