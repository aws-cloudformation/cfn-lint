"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.outputs
from cfnlint.jsonschema import Validator
from cfnlint.jsonschema._keywords import patternProperties
from cfnlint.jsonschema._keywords_cfn import cfn_type
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Configuration(CfnLintJsonSchema):
    """Check Base Outputs Configuration"""

    id = "E6001"
    shortdesc = "Check the properties of Outputs"
    description = "Validate the property structure for outputs"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"
    tags = ["outputs"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Outputs"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.outputs, "configuration.json"
            ),
            all_matches=True,
        )
        self.rule_set = {
            "propertyNames": "E6011",
            "maxLength": "E6011",
            "pattern": "E6004",
            "required": "E6002",
            "type": "E6003",
            "maxProperties": "E6010",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.validators = {
            "type": cfn_type,
            "patternProperties": self._pattern_properties,
        }

    def _pattern_properties(
        self, validator: Validator, pP: Any, instance: Any, schema: Any
    ):
        # We have to rework pattern properties
        # to re-add the keyword or we will have an
        # infinite loop
        validator = validator.evolve(
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=True,
            )
        )

        yield from patternProperties(validator, pP, instance, schema)

    def validate(self, validator: Validator, _: Any, instance: Any, schema: Any):
        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context.evolve(strict_types=False),
        )

        yield from super()._iter_errors(cfn_validator, instance)
