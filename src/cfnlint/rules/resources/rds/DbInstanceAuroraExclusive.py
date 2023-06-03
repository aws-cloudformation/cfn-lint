"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DbInstanceAuroraExclusive(BaseCfnSchema):
    id = "E3682"
    shortdesc = "Validate when using Aurora certain properies aren't required "
    description = (
        "When creating an aurora DBInstance don't specify "
        "'AllocatedStorage', 'BackupRetentionPeriod', 'CopyTagsToSnapshot', "
        "'DeletionProtection', 'EnableIAMDatabaseAuthentication', "
        "'MasterUserPassword', or 'StorageEncrypted'"
    )
    tags = ["resources"]
    schema_path = "aws_rds_dbinstance/aurora_exclusive"
