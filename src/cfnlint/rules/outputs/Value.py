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
    shortdesc = "Outputs have values of strings"
    description = "Making sure the outputs have strings as values"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def __init__(self):
        super().__init__(
            keywords=["Outputs/*/Value"],
            all_matches=True,
        )

    def validate(self, validator: Validator, _: Any, instance: Any, schema: Any):
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=list(FUNCTIONS),
            ),
            schema={"type": "string"},
        )

        yield from self._iter_errors(validator, instance)
