"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class SpotFleetBlockDeviceMappingVirtualName(BaseCfnSchema):
    id = "E3655"
    shortdesc = "Validate SpotFleet block device mapping VirtualName with Ebs"
    description = "When you specify 'VirtualName' do not specify 'Ebs'"
    tags = ["resources"]
    schema_path = "aws_ec2_spotfleet/blockdevicemapping_virtualname"
