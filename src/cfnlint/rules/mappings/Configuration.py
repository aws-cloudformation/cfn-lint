"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.mappings
from cfnlint.jsonschema import Validator
from cfnlint.jsonschema._keywords_cfn import cfn_type
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Configuration(CfnLintJsonSchema):
    """Check if Mappings are configured correctly"""

    id = "E7001"
    shortdesc = "Mappings are appropriately configured"
    description = "Check if Mappings are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html"
    tags = ["mappings"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Mappings"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.mappings, "configuration.json"
            ),
            all_matches=True,
        )
        self.rule_set = {
            "maxProperties": "E7010",
            "maxLength": "E7002",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.validators = {
            "type": cfn_type,
        }

    def validate(self, validator: Validator, _: Any, instance: Any, schema: Any):
        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context.evolve(strict_types=False),
        ).evolve(
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            )
        )

        yield from super()._iter_errors(cfn_validator, instance)
