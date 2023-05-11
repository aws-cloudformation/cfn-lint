"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class AutoScalingGroupLaunchTemplateOnlyOne(BaseCfnSchema):
    id = "E3602"
    shortdesc = "Validate launch template doesn't use exclusive properties together"
    description = "Specify only 'LaunchTemplateId' or 'LaunchTemplateName'"
    tags = ["resources"]
    schema_path = "aws_autoscaling_autoscalinggroup/launchtemplatespecification_onlyone"
