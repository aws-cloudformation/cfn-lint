"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema._keywords import maxLength
from cfnlint.rules import CloudFormationLintRule


class LimitDescription(CloudFormationLintRule):
    """Check Template Description Size"""

    id = "E1003"
    shortdesc = "Validate the max size of a description"
    description = (
        "Check if the size of the template description is less than the upper limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["description", "limits"]

    def __init__(self) -> None:
        super().__init__()
        self.child_rules = {
            "I1003": None,
        }

    def maxLength(
        self, validator: Validator, mL: int, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        errors = list(maxLength(validator, mL, instance, schema))

        if errors:
            yield from iter(errors)
            return

        for child_rule in self.child_rules.values():
            if child_rule is not None:
                if hasattr(child_rule, "maxLength"):
                    yield from child_rule.maxLength(validator, mL, instance, schema)
