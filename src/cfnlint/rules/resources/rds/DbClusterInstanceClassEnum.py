"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_rds_dbcluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class DbClusterInstanceClassEnum(CfnLintJsonSchemaRegional):
    id = "E3694"
    shortdesc = "Validates RDS DB Instance Class"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBCluster/Properties"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.extensions.aws_rds_dbcluster,
                "dbclusterinstanceclass_enum.json",
            ),
        )
