"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SecurityGroupEgressOnlyOne(BaseCfnSchema):
    id = "E3662"
    shortdesc = "Validate SG egress has only one of a set properties"
    description = "Specify only 'CidrIp', 'CidrIpv6', 'DestinationSecurityGroupId', or 'DestinationPrefixListId'"
    tags = ["resources"]
    schema_path = "aws_ec2_securitygroup/egress_onlyone"
