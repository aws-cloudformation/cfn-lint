"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class InstanceBlockDeviceMappingVirtualNameExclusive(BaseCfnSchema):
    id = "E3631"
    shortdesc = "Validate EC2 Instance block device mapping doesn't use " \
        "'VirtualName' with 'Ebs'"
    description = "When you specify 'VirtualName' do not specify 'Ebs'"
    tags = ["resources", "ec2"]
    schema_path = "aws_ec2_instance/blockdevicemapping_virtualname_exclusive"
