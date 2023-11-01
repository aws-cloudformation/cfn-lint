"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema._validators_cfn import FnEquals
from cfnlint.rules import CloudFormationLintRule


class Equals(CloudFormationLintRule):
    """Check Equals Condition Function Logic"""

    id = "E8003"
    shortdesc = "Check Fn::Equals structure for validity"
    description = "Check Fn::Equals is a list of two elements"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-equals"
    tags = ["functions", "equals"]

    def __init__(self) -> None:
        super().__init__()
        self.child_rules = {
            "W8003": None,
        }

    def fn_equals(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        yield from FnEquals().equals(validator, s, instance, schema)

        if self.child_rules.get("W8003"):
            yield from self.child_rules["W8003"].equals_is_useful(
                validator, s, instance.get("Fn::Equals", []), schema
            )
