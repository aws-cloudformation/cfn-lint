"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SpotFleetBlockDeviceMappingOnlyOne(BaseCfnSchema):
    id = "E3653"
    shortdesc = "Validate SpotFleet block device mapping properties"
    description = "Specify only 'VirtualName', 'Ebs', or 'NoDevice'"
    tags = ["resources"]
    schema_path = "aws_ec2_spotfleet/blockdevicemapping_onlyone"
