"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_rds_dbcluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbClusterMultiAz(CfnLintJsonSchema):
    id = "E3692"
    shortdesc = "Validate Multi-AZ DB cluster configuration"
    description = (
        "When creating a Multi-AZ DB Cluster there are required fields and "
        "the allowed values are different"
    )
    tags = ["resources"]
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engineversion"

    def __init__(self) -> None:
        super().__init__(
            keywords=["AWS::RDS::DBCluster/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbcluster,
                filename="multiaz.json",
            ),
            all_matches=True,
        )

    # DBClusterInstanceClass is required
    # AllocatedStorage is required
    # Iops is required
    def validate(self, validator, keywords, instance, schema):
        for err in super().validate(validator, keywords, instance, schema):
            if err.schema is False:
                err.message = (
                    "Additional properties are not allowed "
                    f"{err.path[0]!r} when creating Multi-AZ cluster"
                )

            yield err
