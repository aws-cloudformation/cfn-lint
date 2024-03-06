"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema.protocols import Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class InterfaceParameterExists(CfnLintKeyword):
    """Check if Metadata Interface parameters exist"""

    id = "W4001"
    shortdesc = "Metadata Interface parameters exist"
    description = "Metadata Interface parameters actually exist"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-interface.html"
    tags = ["metadata"]

    valid_keys = ["ParameterGroups", "ParameterLabels"]

    def __init__(self) -> None:
        super().__init__()
        self.keywords = [
            "cfnParameter",
        ]

    def validate(self, validator: Validator, _, instance: Any, schema):
        for err in validator.descend(
            instance, schema={"enum": list(validator.context.parameters.keys())}
        ):
            err.rule = self
            yield err
