"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class LaunchTemplateLaunchTemplateDataSecurityGroupsOnlyOne(BaseCfnSchema):
    id = "E3618"
    shortdesc = (
        "Specify only security groups at the LaunchTemplate or NetworkInterface level"
    )
    description = (
        "Specify only security groups at the LaunchTemplate or NetworkInterface level"
    )
    tags = ["resources"]
    schema_path = "aws_ec2_launchtemplate/launchtemplatedata_securitygroups_onlyone"
