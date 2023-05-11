"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class VpcIpamPool(BaseCfnSchema):
    id = "E3640"
    shortdesc = "Validate VPC IPAM pool has required properties"
    description = "Both 'Ipv4IpamPoolId' and 'Ipv4NetmaskLength' must be provided"
    tags = ["resources"]
    schema_path = "aws_ec2_vpc/ipam_pool"
