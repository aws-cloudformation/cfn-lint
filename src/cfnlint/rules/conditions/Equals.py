"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class Equals(BaseFn):
    """Check Equals Condition Function Logic"""

    id = "E8003"
    shortdesc = "Check Fn::Equals structure for validity"
    description = "Check Fn::Equals is a list of two elements"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-equals"
    tags = ["functions", "equals"]

    def __init__(self) -> None:
        super().__init__("Fn::Equals", ("boolean",))
        self.child_rules = {
            "W8003": None,
        }

    def fn_equals(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        errs = list(self.validate(validator, s, instance, schema))
        if errs:
            yield from iter(errs)
            return

        child_rule = self.child_rules.get("W8003")
        if child_rule and hasattr(child_rule, "equals_is_useful"):
            yield from child_rule.equals_is_useful(
                validator, s, instance.get("Fn::Equals", []), schema
            )

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:
        return {
            "type": "array",
            "maxItems": 2,
            "minItems": 2,
            "fn_items": {
                "functions": [
                    "Ref",
                    "Fn::FindInMap",
                    "Fn::Sub",
                    "Fn::Join",
                    "Fn::Select",
                    "Fn::Split",
                    "Fn::Length",
                    "Fn::ToJsonString",
                ],
                "schema": {
                    "type": ["string"],
                },
            },
        }
