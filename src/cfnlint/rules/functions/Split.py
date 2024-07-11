"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
from collections import deque
from typing import Any

import regex as re

from cfnlint.helpers import REGEX_DYN_REF
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class Split(BaseFn):
    """Check if Split values are correct"""

    id = "E1018"
    shortdesc = "Split validation of parameters"
    description = "Making sure the split function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-split.html"
    tags = ["functions", "split"]

    def __init__(self) -> None:
        super().__init__("Fn::Split", ("array",), resolved_rule="W1033")

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:
        return {
            "type": "array",
            "maxItems": 2,
            "minItems": 2,
            "fn_items": [
                {
                    "schema": {
                        "type": ["string"],
                    }
                },
                {
                    "functions": [
                        "Fn::Base64",
                        "Fn::FindInMap",
                        "Fn::GetAtt",
                        "Fn::GetAZs",
                        "Fn::If",
                        "Fn::ImportValue",
                        "Fn::Join",
                        "Fn::Select",
                        "Fn::Sub",
                        "Ref",
                    ],
                    "schema": {
                        "type": ["string"],
                    },
                },
            ],
        }

    def fn_split(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        errs = list(super().validate(validator, s, instance, schema))
        if errs:
            yield from iter(errs)
            return

        key, value = self.key_value(instance)
        if re.fullmatch(REGEX_DYN_REF, json.dumps(value[1])):
            yield ValidationError(
                f"{key!r} does not support dynamic references",
                validator=self.fn.py,
                path=deque([key, 1]),
            )
