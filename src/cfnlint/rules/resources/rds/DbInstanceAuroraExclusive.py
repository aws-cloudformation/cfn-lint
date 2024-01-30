"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class DbInstanceAuroraExclusive(CfnLintJsonSchema):
    id = "E3682"
    shortdesc = "Validate when using Aurora certain properies aren't required "
    description = (
        "When creating an aurora DBInstance don't specify "
        "'AllocatedStorage', 'BackupRetentionPeriod', 'CopyTagsToSnapshot', "
        "'DeletionProtection', 'EnableIAMDatabaseAuthentication', "
        "'MasterUserPassword', or 'StorageEncrypted'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(keywords=["aws_rds_dbinstance/aurora_exclusive"])
