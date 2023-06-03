"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class InstanceInstanceTypeEnum(BaseCfnRegionSchema):
    id = "E3628"
    shortdesc = "Validate instance types based on region"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = "aws_ec2_instance/instancetype_enum"
