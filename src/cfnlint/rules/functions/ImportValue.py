"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Iterator

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, singular_types


class ImportValue(BaseFn):
    """Check if ImportValue values are correct"""

    id = "E1016"
    shortdesc = "ImportValue validation of parameters"
    description = "Making sure the ImportValue function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-importvalue.html"
    tags = ["functions", "importvalue"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::ImportValue",
            singular_types,
            (
                "Fn::Base64",
                "Fn::FindInMap",
                "Fn::If",
                "Fn::Join",
                "Fn::Select",
                "Fn::Sub",
                "Ref",
            ),
        )
        self.child_rules = {
            "W6001": None,
        }

    def validator(self, validator: Validator) -> Validator:
        return validator.evolve(
            context=validator.context.evolve(
                functions=self.functions,
                resources={},
            ),
        )

    def fn_importvalue(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        errs = list(super().validate(validator, s, instance, schema))
        if errs:
            yield from iter(errs)

        for rule in self.child_rules.values():
            if rule is None:
                continue

            yield from rule.validate(validator, s, instance, schema)
