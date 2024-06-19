"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.other.resources
import cfnlint.helpers
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema._keywords import patternProperties
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Configuration(CfnLintJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3001"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__(
            keywords=["Resources"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.resources, "configuration.json"
            ),
            all_matches=True,
        )
        self.validators = {
            "maxProperties": None,
            "propertyNames": None,
            "patternProperties": self._pattern_properties,
        }
        self.rule_set = {
            "maxProperties": "E3010",
            "propertyNames": "E3011",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))

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
        self, validator: Validator, keywords: Any, instance: Any, schema: Any
    ) -> ValidationResult:

        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context.evolve(),
        )

        yield from self._iter_errors(cfn_validator, instance)
