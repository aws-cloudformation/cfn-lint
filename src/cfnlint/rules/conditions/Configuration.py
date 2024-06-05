"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.other.conditions
from cfnlint.helpers import FUNCTION_CONDITIONS
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails
from cfnlint.schema.resolver import RefResolver


class Configuration(CfnLintJsonSchema):
    """Check if Conditions are configured correctly"""

    id = "E8001"
    shortdesc = "Conditions have appropriate properties"
    description = "Check if Conditions are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html"
    tags = ["conditions"]

    def __init__(self):
        super().__init__(
            keywords=["Conditions"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.conditions,
                "conditions.json",
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, conditions: Any, instance: Any, schema: Any
    ):
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=list(FUNCTION_CONDITIONS) + ["Condition"],
                resources={},
                strict_types=False,
            ),
            schema=self._schema,
            resolver=RefResolver.from_schema(
                self._schema,
            ),
        )

        yield from self._iter_errors(validator, instance)
