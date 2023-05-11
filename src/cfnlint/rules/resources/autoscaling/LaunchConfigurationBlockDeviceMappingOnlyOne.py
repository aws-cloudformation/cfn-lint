"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class LaunchConfigurationBlockDeviceMappingOnlyOne(BaseCfnSchema):
    id = "E3604"
    shortdesc = (
        "Validate launch configuration block device mapping doesn't "
        "use exclusive properties together"
    )
    description = "Specify only 'VirtualName', 'Ebs', or 'NoDevice'"
    tags = ["resources"]
    schema_path = "aws_autoscaling_launchconfiguration/blockdevicemapping_onlyone"
