"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class CfnLintJsonSchemaRegional(CfnLintJsonSchema):
    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        for region in validator.context.regions:
            region_validator = validator.evolve(
                context=validator.context.evolve(regions=[region]),
                schema=self.schema.get(region, True),
            )
            for err in super()._iter_errors(region_validator, instance):
                err.message = err.message + f" in {region!r}"
                yield err
