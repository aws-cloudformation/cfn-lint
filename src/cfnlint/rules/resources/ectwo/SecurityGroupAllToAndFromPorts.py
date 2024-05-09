"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_securitygroup
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class SecurityGroupAllToAndFromPorts(CfnLintJsonSchema):
    id = "E3688"
    shortdesc = "Validate that to and from ports are both -1"
    description = "When ToPort or FromPort are -1 the other one must also be -1"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::SecurityGroup/Properties/SecurityGroupIngress/*",
                "Resources/AWS::EC2::SecurityGroup/Properties/SecurityGroupEgress/*",
                "Resources/AWS::EC2::SecurityGroupEgress/Properties",
                "Resources/AWS::EC2::SecurityGroupIngress/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_ec2_securitygroup,
                filename="all_to_and_from_ports.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return "Both ['FromPort', 'ToPort'] must be -1 when one is -1"
