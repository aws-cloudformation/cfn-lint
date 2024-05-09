"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_ec2_securitygroup
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class SecurityGroupProtocolsAndPortsInclusive(CfnLintJsonSchema):
    id = "E3687"
    shortdesc = "Validate to and from ports based on the protocol"
    description = (
        "When using  icmp, icmpv6, tcp, or udp you have "
        "to specify the to and from port ranges"
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
                filename="protocols_and_port_ranges_include.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "['FromPort', 'ToPort'] are required properties when using "
            f"'IpProtocol' value {instance.get('IpProtocol')!r}"
        )
