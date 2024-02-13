"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Dict

from cfnlint.jsonschema import Validator
from cfnlint.rules.functions._BaseFn import BaseFn, singular_types


class FindInMap(BaseFn):
    """Check if FindInMap values are correct"""

    id = "E1011"
    shortdesc = "FindInMap validation of configuration"
    description = "Making sure the function is a list of appropriate config"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-findinmap.html"
    tags = ["functions", "findinmap"]

    def __init__(self) -> None:
        super().__init__("Fn::FindInMap", ("array",) + singular_types)
        self.fn_findinmap = self.validate

    def schema(self, validator: Validator, instance: Any) -> Dict[str, Any]:
        scalar_schema = {
            "functions": [
                "Fn::FindInMap",
                "Ref",
            ],
            "schema": {
                "type": ["string"],
            },
        }

        schema = {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "fn_items": [
                scalar_schema,
                scalar_schema,
                scalar_schema,
            ],
        }

        if validator.context.transforms.has_language_extensions_transform():
            schema["maxItems"] = 4
            schema["fn_items"] = [
                scalar_schema,
                scalar_schema,
                scalar_schema,
                {
                    "schema": {
                        "type": ["object"],
                        "properties": {
                            "DefaultValue": {
                                "type": ("array",) + singular_types,
                            }
                        },
                        "additionalProperties": False,
                        "required": ["DefaultValue"],
                    }
                },
            ]

        return schema
