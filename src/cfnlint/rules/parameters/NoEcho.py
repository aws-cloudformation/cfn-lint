"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule


class NoEcho(CloudFormationLintRule):
    id = "W2010"
    shortdesc = "NoEcho parameters are not masked when used in Metadata and Outputs"
    description = (
        "Using the NoEcho attribute does not mask any information stored "
        "in the following: Metadata, Outputs, Resource Metadata"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html"
    tags = ["functions", "dynamic reference", "ref"]

    def validate(self, validator: Validator, _, instance: Any, schema: Any):
        value = instance.get("Ref")

        if not validator.is_type(value, "string"):
            return

        parameter = validator.context.parameters.get(value)
        if not parameter:
            return

        if parameter.no_echo:
            if len(validator.context.path) >= 3:
                if (
                    validator.context.path[0] == "Resources"
                    and validator.context.path[2] == "Metadata"
                ):
                    yield ValidationError(
                        f"Don't use 'NoEcho' parameter {value!r} in resource metadata",
                        rule=self,
                        path=deque(["Ref"]),
                    )
                    return
            if len(validator.context.path) > 0:
                if validator.context.path[0] in ["Metadata", "Outputs"]:
                    yield ValidationError(
                        (
                            f"Don't use 'NoEcho' parameter {value!r} "
                            f"in {validator.context.path[0]!r}"
                        ),
                        rule=self,
                        path=deque(["Ref"]),
                    )
                    return
