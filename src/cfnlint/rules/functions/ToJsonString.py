"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import TRANSFORM_LANGUAGE_EXTENSION
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class ToJsonString(BaseFn):
    """Check if ToJsonString values are correct"""

    id = "E1031"
    shortdesc = "ToJsonString validation of parameters"
    description = "Making sure Fn::ToJsonString is configured correctly"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html"
    tags = ["functions", "toJsonString"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::ToJsonString",
            ("string",),
            resolved_rule="W1040",
        )

    def fn_tojsonstring(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.context.transforms.has_language_extensions_transform():
            yield ValidationError(
                (
                    f"{self.fn.name} is not supported without "
                    f"{TRANSFORM_LANGUAGE_EXTENSION!r} transform"
                ),
                validator=self.fn.py,
                rule=self,
            )
            return

        for err in super().validate(validator, s, instance, schema):
            err.rule = self
            yield err
