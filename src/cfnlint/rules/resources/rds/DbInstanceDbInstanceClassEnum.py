"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class DbInstanceDbInstanceClassEnum(BaseCfnRegionSchema):
    id = "E3683"
    shortdesc = "Validates RDS DB Instance Class"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = "aws_rds_dbinstance/dbinstanceclass_enum"
