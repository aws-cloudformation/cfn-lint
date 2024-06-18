"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.rules.functions._BaseFn import BaseFn


class Condition(BaseFn):
    """Check And Condition Function Logic"""

    id = "E8007"
    shortdesc = "Check Condition structure for validity"
    description = "Check Condition has a value of another condition"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-and"
    tags = ["functions", "and"]

    def __init__(self) -> None:
        super().__init__("Condition", ("boolean",))
        self.condition = self.validate

    def schema(self, validator, instance) -> dict[str, Any]:
        return {
            "type": "string",
            "enum": list(validator.context.conditions.conditions.keys()),
        }
