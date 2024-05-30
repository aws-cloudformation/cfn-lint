"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_neptune_dbinstance
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DBInstanceDBInstanceClassEnum(CfnLintJsonSchemaRegional):
    id = "E3635"
    shortdesc = "Validate Neptune DB instance class"
    description = (
        "Validates the instance types for Neptune DB based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Neptune::DBInstance/Properties/DBInstanceClass"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_neptune_dbinstance,
                filename="dbinstanceclass_enum.json",
            ),
        )
