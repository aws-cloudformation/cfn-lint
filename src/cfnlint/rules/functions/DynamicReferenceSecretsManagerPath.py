"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule


class DynamicReferenceSecretsManagerPath(CloudFormationLintRule):
    id = "E1051"
    shortdesc = (
        "Validate dynamic references to secrets manager are only in resource properties"
    )
    description = (
        "Dynamic references from secrets manager can only be used "
        "in resource properties"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html#dynamic-references-secretsmanager"
    tags = ["functions", "dynamic reference"]

    def validate(self, validator: Validator, s: Any, instance: Any, schema: Any):
        if len(validator.context.path.path) >= 3:
            if (
                validator.context.path.path[0] == "Resources"
                and validator.context.path.path[2] == "Properties"
            ):
                return

        yield ValidationError(
            (
                f"Dynamic reference {instance!r} to secrets manager can only be "
                "used in resource properties"
            ),
            rule=self,
        )
