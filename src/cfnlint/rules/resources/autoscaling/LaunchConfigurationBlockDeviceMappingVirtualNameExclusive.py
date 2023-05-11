"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class LaunchConfigurationBlockDeviceMappingVirtualNameExclusive(BaseCfnSchema):
    id = "E3605"
    shortdesc = (
        "Validate launch configuration block device mapping virtual name doesn't "
        "include Ebs"
    )
    description = "When you specify 'VirtualName' do not specify 'Ebs'"
    tags = ["resources"]
    schema_path = (
        "aws_autoscaling_launchconfiguration/blockdevicemapping_virtualname_exlusive"
    )
