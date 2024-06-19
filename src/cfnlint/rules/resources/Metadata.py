"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.other.resources
import cfnlint.helpers
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.jsonschema._keywords import additionalProperties, properties
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class Metadata(CfnLintJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3028"
    shortdesc = "Validate the metadata section of a resource"
    description = (
        "The metadata section can be unstructured but we do "
        "validate the items we can"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__(
            keywords=["Resources/*/Metadata"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.resources, "metadata.json"
            ),
            all_matches=True,
        )
        self.validators["properties"] = self._properties
        self.validators["additionalProperties"] = self._additional_properties

    def _properties(self, validator: Validator, pP: Any, instance: Any, schema: Any):
        # We have to rework pattern properties
        # to re-add the keyword or we will have an
        # infinite loop
        validator = validator.evolve(
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=True,
            )
        )

        yield from properties(validator, pP, instance, schema)

    def _additional_properties(
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

        yield from additionalProperties(validator, pP, instance, schema)

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context.evolve(
                functions=cfnlint.helpers.FUNCTIONS,
                strict_types=False,
            ),
        )

        yield from self._iter_errors(validator, instance)
