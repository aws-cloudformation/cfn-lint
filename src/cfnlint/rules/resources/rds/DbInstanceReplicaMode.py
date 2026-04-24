"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceReplicaMode(CfnLintJsonSchema):
    id = "E3721"
    shortdesc = "Validate ReplicaMode value for Oracle and Db2 engines"
    description = (
        "When specifying ReplicaMode for Oracle or Db2 engines, "
        "the value must be 'mounted' or 'open-read-only'."
    )
    source_url = "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/oracle-read-replicas.html"
    tags = ["resources", "rds"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::RDS::DBInstance/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="replicamode_enum.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
