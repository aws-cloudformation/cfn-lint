"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceBackupRetentionPeriod(CfnLintJsonSchema):
    id = "E3719"
    shortdesc = "Validate RDS BackupRetentionPeriod based on instance configuration"
    description = (
        "BackupRetentionPeriod maximum of 35 applies to standalone "
        "non-Aurora instances. Read replicas and Aurora instances "
        "inherit backup settings and ignore this property."
    )
    source_url = "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html"
    tags = ["resources", "rds"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::RDS::DBInstance/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="backupretentionperiod.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            f"BackupRetentionPeriod {instance.get('BackupRetentionPeriod')} "
            f"exceeds maximum of 35 for non-Aurora standalone instances"
        )
