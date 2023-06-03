"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class FleetInstanceTypeEnum(BaseCfnRegionSchema):
    id = "E3621"
    shortdesc = "Validate the instance types for AppStream Fleet"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = "aws_appstream_fleet/instancetype_enum"
