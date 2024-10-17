"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class Value(CfnLintJsonSchema):
    """Check if Outputs have string values"""

    id = "E6101"
    shortdesc = "Validate that outputs values are a string"
    description = "Make sure that output values have a type of string"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def __init__(self):
        super().__init__(
            keywords=["Outputs/*"],
            all_matches=True,
        )

    def validate(self, validator: Validator, _: Any, instance: Any, schema: Any):
        key = "Value"
        value = instance.get(key)
        if not value:
            return

        conditions = {}
        condition = instance.get("Condition")
        if condition:
            conditions = {condition: True}

        validator = validator.evolve(
            context=validator.context.evolve(
                functions=list(FUNCTIONS),
                conditions=validator.context.conditions.evolve(
                    conditions,
                ),
                strict_types=False,
            )
        )

        for err in validator.descend(
            value,
            schema={
                "type": ["string"],
            },
            path=key,
            property_path=key,
        ):
            if err.rule is None:
                err.rule = self
            yield err
