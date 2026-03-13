"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.constants
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Configuration(CfnLintJsonSchema):
    """Check if Constants are configured correctly"""

    id = "E1060"
    shortdesc = "Constants are appropriately configured"
    description = "Check if Constants are properly configured"
    # TODO: Update source_url once Constants documentation is published
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/template-anatomy.html"
    tags = ["constants"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Constants"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.constants, "configuration.json"
            ),
            all_matches=True,
        )

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
