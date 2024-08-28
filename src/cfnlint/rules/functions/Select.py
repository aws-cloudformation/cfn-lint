"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules.functions._BaseFn import BaseFn, all_types


class Select(BaseFn):
    """Check if Select values are correct"""

    id = "E1017"
    shortdesc = "Select validation of parameters"
    description = "Making sure the Select function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-select.html"
    tags = ["functions", "select"]

    def __init__(self) -> None:
        super().__init__("Fn::Select", all_types, resolved_rule="W1035")
        self.fn_select = self.validate

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:
        schema = {
            "type": "array",
            "maxItems": 2,
            "minItems": 2,
            "fn_items": [
                {
                    "functions": ["Ref", "Fn::FindInMap"],
                    "schema": {
                        "type": ["integer"],
                    },
                },
                {
                    "functions": [
                        "Fn::FindInMap",
                        "Fn::GetAtt",
                        "Fn::GetAZs",
                        "Fn::If",
                        "Fn::Split",
                        "Fn::Cidr",
                        "Ref",
                    ],
                    "schema": {
                        "type": ["array"],
                        "fn_items": {
                            "functions": [
                                "Fn::FindInMap",
                                "Fn::GetAtt",
                                "Fn::If",
                                "Ref",
                            ],
                            "schema": {
                                "type": all_types,
                            },
                        },
                    },
                },
            ],
        }

        if validator.context.transforms.has_language_extensions_transform():
            schema["fn_items"][0]["functions"].append("Fn::Length")  # type: ignore

        return schema
