"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DbInstanceSourceDbInstanceIdentifierExclusive(BaseCfnSchema):
    id = "E3681"
    shortdesc = (
        "Validate when restoring an RDS instance from a source "
        "DB certain properties are not needed"
    )
    description = (
        "When you specify 'SourceDBInstanceIdentifier' do not "
        "specify 'CharacterSetName', 'MasterUsername', "
        "'MasterUserPassword', or 'StorageEncrypted'"
    )
    tags = ["resources"]
    schema_path = "aws_rds_dbinstance/sourcedbinstanceidentifier_exclusive"
