"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.parameters
from cfnlint.jsonschema import Validator
from cfnlint.jsonschema._keywords import patternProperties
from cfnlint.jsonschema._keywords_cfn import cfn_type
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Configuration(CfnLintJsonSchema):
    """Check if Parameters are configured correctly"""

    id = "E2001"
    shortdesc = "Parameters have appropriate properties"
    description = "Making sure the parameters are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html"
    tags = ["parameters"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Parameters"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.parameters, "configuration.json"
            ),
            all_matches=True,
        )
        self.rule_set = {
            "maxLength": "E2011",
            "maxProperties": "E2010",
            "minProperties": "E2010",
            "pattern": "E2003",
            "enum": "E2002",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
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
                add_cfn_lint_keyword=False,
            )
        )
        yield from patternProperties(validator, aP, instance, schema)

    def validate(self, validator: Validator, _: Any, instance: Any, schema: Any):
        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context,
        ).evolve(
            context=validator.context.evolve(strict_types=False),
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            ),
        )

        for err in super()._iter_errors(cfn_validator, instance):
            # we use enum twice.  Once for the type and once for the property
            # names.  There are separate error numbers so we do this.
            if "propertyNames" in err.schema_path and "enum" in err.schema_path:
                err.rule = self
            yield err
