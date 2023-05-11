"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class LaunchTemplateBlockDeviceMappingVirtualName(BaseCfnSchema):
    id = "E3619"
    shortdesc = "Validate launch template block device mapping doesn't use exlusive properties"
    description = "When you specify 'VirtualName' do not specify 'Ebs'"
    tags = ["resources"]
    schema_path = "aws_ec2_launchtemplate/blockdevicemapping_virtualname"
