"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class And(BaseFn):
    """Check And Condition Function Logic"""

    id = "E8004"
    shortdesc = "Check Fn::And structure for validity"
    description = "Check Fn::And is a list of two elements"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-and"
    tags = ["functions", "and"]

    def __init__(self) -> None:
        super().__init__("Fn::And", ("boolean",))
        self.fn_and = self.validate

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:
        return {
            "type": "array",
            "minItems": 2,
            "maxItems": 10,
            "fn_items": {
                "functions": [
                    "Condition",
                    "Fn::Equals",
                    "Fn::Not",
                    "Fn::And",
                    "Fn::Or",
                ],
                "schema": {
                    "type": ["boolean"],
                },
            },
        }
