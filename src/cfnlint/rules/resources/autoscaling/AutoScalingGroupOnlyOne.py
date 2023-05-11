"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class AutoScalingGroupOnlyOne(BaseCfnSchema):
    id = "E3603"
    shortdesc = "Validate auto scaling group doesn't use exlusive properties together"
    description = "Specify only 'InstanceId', 'LaunchConfigurationName', 'LaunchTemplate', or 'MixedInstancesPolicy'"
    tags = ["resources"]
    schema_path = "aws_autoscaling_autoscalinggroup/onlyone"
