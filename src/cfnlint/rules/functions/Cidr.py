"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class Cidr(BaseFn):
    """Check if Cidr values are correct"""

    id = "E1024"
    shortdesc = "Cidr validation of parameters"
    description = "Making sure the function CIDR is a list with valid values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-cidr.html"
    tags = ["functions", "cidr"]

    def __init__(self) -> None:
        super().__init__("Fn::Cidr", ("array",), None)
        self.fn_cidr = self.validate

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:
        functions = [
            "Fn::FindInMap",
            "Fn::Select",
            "Ref",
            "Fn::GetAtt",
            "Fn::Sub",
            "Fn::ImportValue",
            "Fn::If",
        ]
        return {
            "type": ["array"],
            "maxItems": 3,
            "minItems": 2,
            "fn_items": [
                {
                    "functions": functions,
                    "schema": {
                        "type": ["string"],
                        "pattern": (
                            "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.)"
                            "{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
                            "(\\/([0-9]|[1-2][0-9]|3[0-2]))$"
                        ),
                    },
                },
                {
                    "functions": functions,
                    "schema": {
                        "type": ["integer"],
                        "minimum": 1,
                        "maximum": 256,
                    },
                },
                {
                    "functions": functions,
                    "schema": {
                        "type": ["integer"],
                        "minimum": 1,
                        "maximum": 128,
                    },
                },
            ],
        }
