"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class InstanceBlockDeviceMappingOnlyOne(BaseCfnSchema):
    id = "E3630"
    shortdesc = "Validate EC2 Instance block device mapping doesn't use " \
        "exclusive properties"
    description = "Specify only 'VirtualName', 'Ebs', or 'NoDevice'"
    tags = ["resources"]
    schema_path = "aws_ec2_instance/blockdevicemapping_onlyone"
