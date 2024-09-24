"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import FUNCTION_RULES
from cfnlint.jsonschema import Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class Not(BaseFn):
    """Check Not Condition Function Logic"""

    id = "E8005"
    shortdesc = "Check Fn::Not structure for validity"
    description = "Check Fn::Not is a list of one element"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#intrinsic-function-reference-conditions-not"
    tags = ["functions", "not"]

    def __init__(self) -> None:
        super().__init__("Fn::Not", ("boolean",))
        self.fn_not = self.validate

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:

        if validator.context.path.path and validator.context.path.path[0] == "Rules":
            functions = list(FUNCTION_RULES)
        else:
            functions = [
                "Condition",
                "Fn::Equals",
                "Fn::Not",
                "Fn::And",
                "Fn::Or",
            ]

        return {
            "type": "array",
            "maxItems": 1,
            "minItems": 1,
            "fn_items": {
                "functions": functions,
                "schema": {
                    "type": ["boolean"],
                },
            },
        }
