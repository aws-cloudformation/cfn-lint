"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional



class DBInstanceClassEnum(CfnLintJsonSchemaRegional):
    id = "E3620"
    shortdesc = "Validate a DocDB DB Instance class"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(["aws_docdb_dbinstance/dbinstanceclass_enum"])

