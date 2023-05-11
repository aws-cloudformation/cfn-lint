"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class ScalingPolicyScalingPolicy(BaseCfnSchema):
    id = "E3648"
    shortdesc = "Validate application auto scaling properties are properly configured"
    description = "You must specify either the ScalingTargetId property, or the ResourceId, ScalableDimension, and ServiceNamespace properties, but not both."
    tags = ["resources"]
    schema_path = "aws_applicationautoscaling_scalingpolicy/scalingpolicy"
