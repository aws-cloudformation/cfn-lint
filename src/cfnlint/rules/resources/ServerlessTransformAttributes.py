"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.helpers import TRANSFORM_SAM
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class ServerlessTransformAttributes(CfnLintKeyword):
    """Check if SAM resource attributes exist without the Serverless Transform"""

    id = "E3066"
    shortdesc = "SAM resource attributes require the Serverless Transform"
    description = (
        "Connectors and IgnoreGlobals are SAM resource attributes "
        "that require the Serverless Transform to be declared"
    )
    source_url = "https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/managing-permissions-connectors.html"
    tags = ["resources", "transform"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/*/Connectors",
                "Resources/*/IgnoreGlobals",
            ]
        )

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if validator.cfn.has_serverless_transform():
            return

        attribute = validator.context.path.path[-1]
        yield ValidationError(
            f"{attribute!r} is a SAM resource attribute that requires "
            f"the serverless transform {TRANSFORM_SAM!r}",
            rule=self,
        )
