"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import PSEUDOPARAMS
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
            (
                "Fn::FindInMap",
                "Fn::GetAtt",
                "Fn::GetAZs",
                "Fn::If",
                "Fn::Select",
                "Fn::Split",
                "Ref",
            ),
            resolved_rule="W1040",
        )

    def schema(self, validator: Validator, instance: Any) -> dict[str, Any]:
        return {
            "type": ["array", "object"],
            "minItems": 1,
            "minProperties": 1,
        }

    def validator(self, validator: Validator) -> Validator:
        return validator.evolve(
            context=validator.context.evolve(
                functions=self.functions,
                pseudo_parameters=set(
                    [sp for sp in PSEUDOPARAMS if sp != "AWS::NotificationARNs"]
                ),
            ),
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            ),
        )

    def fn_tojsonstring(
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
