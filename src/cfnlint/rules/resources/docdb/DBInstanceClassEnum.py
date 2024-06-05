"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_docdb_dbinstance
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DBInstanceClassEnum(CfnLintJsonSchemaRegional):
    id = "E3620"
    shortdesc = "Validate a DocDB DB Instance class"
    description = (
        "Validates the DocDB instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::DocDB::DBInstance/Properties/DBInstanceClass"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_docdb_dbinstance,
                filename="dbinstanceclass_enum.json",
            ),
        )
