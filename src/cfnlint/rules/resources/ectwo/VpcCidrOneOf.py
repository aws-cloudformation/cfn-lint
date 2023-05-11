"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class VpcCidrOneOf(BaseCfnSchema):
    id = "E3639"
    shortdesc = (
        "Validate VPC has one of the required properties specified"
    )
    description = (
        "Either CIDR Block or IPv4 IPAM Pool and IPv4 Netmask Length must be provided"
    )
    tags = ["resources"]
    schema_path = "aws_ec2_vpc/cidr_oneof"
