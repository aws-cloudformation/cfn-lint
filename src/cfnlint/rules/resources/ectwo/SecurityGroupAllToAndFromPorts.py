"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class SecurityGroupAllToAndFromPorts(CfnLintJsonSchema):
    id = "E3688"
    shortdesc = "Validate that to and from ports are both -1"
    description = "When ToPort or FromPort are -1 the other one must also be -1"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(keywords=["aws_ec2_securitygroup/all_to_and_from_ports"])

    def message(self, instance: Any, err: ValidationError) -> str:
        if not isinstance(instance, dict):
            return self.description

        return "Both ['FromPort', 'ToPort'] must be -1 when one is -1"
