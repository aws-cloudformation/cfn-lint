"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.jsonschema import ValidationResult
from cfnlint.jsonschema.protocols import Validator
from cfnlint.rules.jsonschema import CfnLintJsonSchema, SchemaDetails


class FunctionEnvironmentKeys(CfnLintJsonSchema):

    id = "E3663"
    shortdesc = "Validate Lambda environment variable names aren't reserved"
    description = (
        "Lambda reserves a set of environment variable names for its use. "
        "This rule validates that the provided environment variable names "
        "don't use the reserved variable names"
    )
    source_url = (
        "https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html"
    )
    tags = ["resources", "lambda", "runtime"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=[
                "Resources/AWS::Lambda::Function/Properties/Environment/Variables"
            ],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.extensions.aws_lambda_function,
                "environment_variable_keys.json",
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        for err in super().validate(validator, keywords, instance, schema):
            err.message = (
                f"{err.instance!r} is a reserved variable name, one of "
                f"{self.schema.get('propertyNames').get('not').get('enum')!r}"
            )
            yield err
