"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules import CloudFormationLintRule


class ApproachingLimitDescription(CloudFormationLintRule):
    """Check Template Description Size"""

    id = "I1003"
    shortdesc = "Validate if we are approaching the max size of a description"
    description = (
        "Check if the size of the template description is approaching the upper limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["description", "limits"]

    def __init__(self) -> None:
        super().__init__()
        self.config["threshold"] = 0.9

    def maxLength(
        self, validator: Validator, mL: int, instance: Any, schema: Any
    ) -> ValidationResult:
        if len(instance) > mL * self.config.get("threshold", 1):
            yield ValidationError(
                f"{instance!r} is approaching the max length of {mL}",
                rule=self,
            )
