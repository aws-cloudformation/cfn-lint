"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_securitygroup
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class SecurityGroupProtocolsAndPortsExclusive(CfnLintJsonSchema):
    id = "W3687"
    shortdesc = "Validate that ports aren't specified for certain protocols"
    description = (
        "When using a protocol other than icmp, icmpv6, tcp, or udp "
        "the port ranges properties are ignored"
    )
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
                filename="protocols_and_port_ranges_exclude.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "['FromPort', 'ToPort'] are ignored when using "
            f"'IpProtocol' value {instance.get('IpProtocol')!r}"
        )
