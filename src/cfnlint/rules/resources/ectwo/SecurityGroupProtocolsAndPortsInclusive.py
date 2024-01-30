"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


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
            keywords=["aws_ec2_securitygroup/protocols_and_port_ranges_include"]
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        if not isinstance(instance, dict):
            return self.description

        return (
            "['FromPort', 'ToPort'] is a required property when using "
            f"'IpProtocol' value {instance.get('IpProtocol')!r}"
        )
