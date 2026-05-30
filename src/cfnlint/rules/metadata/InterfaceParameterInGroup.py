"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class InterfaceParameterInGroup(CfnLintKeyword):
    """Check that all Parameters are listed in Metadata Interface ParameterGroups"""

    id = "W4002"
    shortdesc = "Parameter not listed in Metadata Interface ParameterGroups"
    description = (
        "All parameters should be listed in at least one "
        "Metadata AWS::CloudFormation::Interface ParameterGroup so they appear "
        "in the CloudFormation Console UI"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudformation-interface.html"
    tags = ["metadata"]

    def __init__(self) -> None:
        super().__init__(keywords=["Metadata/AWS::CloudFormation::Interface"])

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        if not isinstance(instance, dict):
            return

        grouped: set[str] = set()
        for group in instance.get("ParameterGroups", []):
            if isinstance(group, dict):
                for param in group.get("Parameters", []):
                    if isinstance(param, str):
                        grouped.add(param)

        for param_name in validator.context.parameters:
            if param_name not in grouped:
                yield ValidationError(
                    f"Parameter {param_name!r} is not listed in any "
                    "Metadata AWS::CloudFormation::Interface ParameterGroup",
                    rule=self,
                )
