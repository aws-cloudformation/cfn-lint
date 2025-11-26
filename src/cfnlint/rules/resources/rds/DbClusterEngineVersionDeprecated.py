"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_rds_dbcluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbClusterEngineVersionDeprecated(CfnLintJsonSchema):
    id = "W3690"
    shortdesc = "Validate DB Cluster Engine Version is not deprecated"
    description = (
        "Validate the DB Cluster engine version is not deprecated and can be "
        "used to create new instances"
    )
    tags = ["resources"]
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engineversion"

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBCluster/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbcluster,
                filename="engine_version_deprecated.json",
            ),
            all_matches=False,
        )

    def message(self, instance, err):
        engine = instance.get("Engine", "")
        engine_version = instance.get("EngineVersion", "")
        return (
            f"Engine version '{engine_version}' for engine '{engine}' is "
            f"deprecated and cannot be used to create new RDS DB clusters"
        )
