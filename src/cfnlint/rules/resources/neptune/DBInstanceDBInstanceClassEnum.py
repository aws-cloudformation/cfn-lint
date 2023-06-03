"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class DBInstanceDBInstanceClassEnum(BaseCfnRegionSchema):
    id = "E3635"
    shortdesc = "Validate Neptune DB instance class"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = "aws_neptune_dbinstance/dbinstanceclass_enum"
