"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SecurityGroupProtocolsAndPorts(BaseCfnSchema):
    id = "E3687"
    shortdesc = "Validate to and from ports based on the protocol"
    description = (
        "When using icmp,icmpv6,tcp, or udp you have "
        "to specify the to and from port ranges"
    )
    tags = ["resources"]
    schema_path = "aws_ec2_securitygroup/protocols_and_port_ranges"

    def message(self, err: ValidationError) -> str:
        if not isinstance(err.instance, dict):
            return self.description

        return (
            f"['FromPort', 'ToPort'] is a required property when using "
            f"'IpProtocol' value {err.instance.get('IpProtocol')!r}"
        )
