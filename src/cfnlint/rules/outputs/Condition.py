"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class Condition(CfnLintJsonSchema):

    id = "E6005"
    shortdesc = "Validate the Output condition is valid"
    description = (
        "Check the condition of an output to make sure it exists inside the template"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs", "conditions"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Outputs/*/Condition"],
            all_matches=True,
        )

    def validate(self, validator: Validator, _, instance: Any, schema):
        if not validator.is_type(instance, "string"):
            return

        validator = self.extend_validator(
            validator=validator,
            schema={"enum": list(validator.context.conditions.conditions.keys())},
            context=validator.context.evolve(),
        )

        yield from self._iter_errors(validator, instance)
