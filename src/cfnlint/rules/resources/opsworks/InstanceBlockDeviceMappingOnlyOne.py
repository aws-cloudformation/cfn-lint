"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class InstanceBlockDeviceMappingOnlyOne(BaseCfnSchema):
    id = "E3658"
    shortdesc = (
        "Validate block device mappings don't have exclusive " "properties specified"
    )
    description = "Specify only 'VirtualName', 'Ebs', or 'NoDevice'"
    tags = ["resources"]
    schema_path = "aws_opsworks_instance/blockdevicemapping_onlyone"
