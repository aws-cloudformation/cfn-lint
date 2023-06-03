"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class FleetEc2InstanceTypeEnum(BaseCfnRegionSchema):
    id = "E3641"
    shortdesc = "Validate GameLift Fleet EC2 instance type"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = "aws_gamelift_fleet/ec2instancetype_enum"
