"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Dict

from cfnlint.rules.functions._BaseFn import BaseFn


class Join(BaseFn):
    """Check if Join values are correct"""

    id = "E1022"
    shortdesc = "Join validation of parameters"
    description = "Making sure the join function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-join.html"
    tags = ["functions", "join"]

    def __init__(self) -> None:
        super().__init__("Fn::Join", ("string",))
        self.fn_join = self.validate

    def schema(self, validator, instance) -> Dict[str, Any]:
        return {
            "type": "array",
            "maxItems": 2,
            "minItems": 2,
            "fn_items": [
                {
                    "schema": {
                        "type": ["string"],
                    },
                },
                {
                    "functions": [
                        "Fn::FindInMap",
                        "Fn::If",
                        "Fn::Split",
                        "Ref",
                    ],
                    "schema": {
                        "type": ["array"],
                        "fn_items": {
                            "functions": [
                                "Fn::Base64",
                                "Fn::FindInMap",
                                "Fn::GetAtt",
                                "Fn::If",
                                "Fn::ImportValue",
                                "Fn::Join",
                                "Fn::Select",
                                "Fn::Sub",
                                "Fn::Transform",
                                "Ref",
                            ],
                            "schema": {
                                "type": ["string"],
                            },
                        },
                    },
                },
            ],
        }
