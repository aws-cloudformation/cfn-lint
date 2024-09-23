"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.helpers import FUNCTION_RULES
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class Assert(CfnLintJsonSchema):
    id = "E1701"
    shortdesc = "Validate the configuration of Assertions"
    description = "Make sure the Assert value in a Rule is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/rules-section-structure.html"
    tags = ["rules"]

    def __init__(self):
        super().__init__(
            keywords=["Rules/*/Assertions/*/Assert"],
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=list(FUNCTION_RULES) + ["Condition"],
            ),
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            ),
            schema={"type": "boolean"},
        )

        yield from self._iter_errors(validator, instance)
