"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceEngineVersionDeprecated(CfnLintJsonSchema):
    id = "W3691"
    shortdesc = "Validate DB Instance Engine Version is not deprecated"
    description = (
        "Validate the DB Instance engine version is not deprecated and can be "
        "used to create new instances"
    )
    tags = ["resources"]
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbinstance.html#cfn-rds-dbinstance-engineversion"

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBInstance/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="engine_version_deprecated.json",
            ),
            all_matches=False,
        )

    def message(self, instance, err):
        engine = instance.get("Engine", "")
        engine_version = instance.get("EngineVersion", "")
        return (
            f"Engine version '{engine_version}' for engine '{engine}' is "
            f"deprecated and cannot be used to create new RDS DB instances"
        )
