"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceBackupRetentionPeriod(CfnLintJsonSchema):
    id = "E3719"
    shortdesc = "Validate RDS BackupRetentionPeriod configuration"
    description = (
        "BackupRetentionPeriod is not allowed when DBClusterIdentifier "
        "is specified. For standalone non-Aurora instances the maximum "
        "is 35."
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
                filename="backupretentionperiod_maximum.json",
            ),
            all_matches=True,
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        for err in super().validate(validator, keywords, instance, schema):
            if err.schema is False:
                err.message = (
                    "'BackupRetentionPeriod' is not allowed when "
                    "'DBClusterIdentifier' is specified. Set backup "
                    "retention period on the DB cluster instead."
                )
            yield err
