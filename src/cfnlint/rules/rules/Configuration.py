"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.rules
from cfnlint.jsonschema import Validator
from cfnlint.jsonschema._keywords import patternProperties
from cfnlint.jsonschema._keywords_cfn import cfn_type
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Configuration(CfnLintJsonSchema):
    id = "E1700"
    shortdesc = "Rules have the appropriate configuration"
    description = "Making sure the Rules section is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/rules-section-structure.html"
    tags = ["rules"]

    def __init__(self):
        super().__init__(
            keywords=["Rules"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.rules, "configuration.json"
            ),
            all_matches=True,
        )
        self.validators = {
            "type": cfn_type,
            "patternProperties": self._pattern_properties,
        }

    def _pattern_properties(
        self, validator: Validator, aP: Any, instance: Any, schema: Any
    ):
        # We have to rework pattern properties
        # to re-add the keyword or we will have an
        # infinite loop
        validator = validator.evolve(
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=True,
            )
        )
        yield from patternProperties(validator, aP, instance, schema)

    def validate(
        self, validator: Validator, conditions: Any, instance: Any, schema: Any
    ):
        rule_validator = self.extend_validator(
            validator=validator,
            schema=self.schema,
            context=validator.context.evolve(
                resources={},
                strict_types=False,
            ),
        ).evolve(
            context=validator.context.evolve(strict_types=False),
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            ),
        )

        yield from super()._iter_errors(rule_validator, instance)
