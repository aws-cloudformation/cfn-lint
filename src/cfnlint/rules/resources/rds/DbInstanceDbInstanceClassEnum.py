"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DbInstanceDbInstanceClassEnum(CfnLintJsonSchemaRegional):
    id = "E3025"
    shortdesc = "Validates RDS DB Instance Class"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["AWS::RDS::DBInstance/Properties"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                "dbinstanceclass_enum.json",
            ),
        )
