"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class Length(BaseFn):
    """Check if Length values are correct"""

    id = "E1030"
    shortdesc = "Length validation of parameters"
    description = "Making sure Fn::Length is configured correctly"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-length.html"
    tags = ["functions", "length"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::Length",
            ("integer",),
        )

    def fn_length(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.context.transforms.has_language_extensions_transform():
            yield ValidationError(
                (
                    f"{self.fn.name} is not supported without "
                    "'AWS::LanguageExtensions' transform"
                ),
                validator=self.fn.py,
                rule=self,
            )
            return

        for err in super().validate(validator, s, instance, schema):
            err.rule = self
            yield err
