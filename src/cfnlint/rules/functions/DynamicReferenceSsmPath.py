"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule


class DynamicReferenceSsmPath(CloudFormationLintRule):
    id = "E1052"
    shortdesc = "Validate dynamic references to SSM are in a valid location"
    description = (
        "Dynamic references to SSM parameters are only supported "
        "in certain locations"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html#dynamic-references-ssm"
    tags = ["functions", "dynamic reference"]

    def validate(self, validator: Validator, s: Any, instance: Any, schema: Any):
        if len(validator.context.path.path) > 0:
            if validator.context.path.path[0] == "Parameters":
                if len(validator.context.path.path) >= 3:
                    if validator.context.path.path[2] in ["Default", "AllowedValues"]:
                        return
            elif validator.context.path.path[0] == "Resources":
                if len(validator.context.path.path) >= 3:
                    if validator.context.path.path[2] in ["Properties", "Metadata"]:
                        return
            elif validator.context.path.path[0] == "Outputs":
                if len(validator.context.path.path) >= 3:
                    if validator.context.path.path[2] in ["Value"]:
                        return

        yield ValidationError(
            (f"Dynamic reference {instance!r} to SSM parameters are not allowed here"),
            rule=self,
        )
