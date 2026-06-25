"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.other.sam
from cfnlint.helpers import TRANSFORM_SAM
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class GlobalsTransform(CfnLintJsonSchema):
    """Check if Globals section exists without the Serverless Transform"""

    id = "E3724"
    shortdesc = "Validate Globals section"
    description = (
        "The Globals section is only valid in SAM templates. "
        "Check that the Serverless transform is declared and "
        "validate the Globals section structure."
    )
    source_url = "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/sam-specification-template-anatomy-globals.html"
    tags = ["resources", "transform", "serverless"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Globals"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.other.sam, "globals.json"
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        if not validator.cfn.has_serverless_transform():
            yield ValidationError(
                f"'Globals' section requires the serverless "
                f"transform {TRANSFORM_SAM!r}",
                rule=self,
            )
            return

        # Validate the Globals section structure against the schema
        cfn_validator = self.extend_validator(
            validator=validator,
            schema=self._schema,
            context=validator.context.evolve(),
        )
        yield from self._iter_errors(cfn_validator, instance)
