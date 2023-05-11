"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DbClusterSourceDbClusterIdentifierExclusive(BaseCfnSchema):
    id = "E3685"
    shortdesc = (
        "Validate when restoring a DB from a point in time "
        "certain properties are not required"
    )
    description = (
        "When you specify 'SourceDBClusterIdentifier' do "
        "not specify 'StorageEncrypted', 'MasterUsername', or "
        "'MasterUserPassword'"
    )
    tags = ["resources"]
    schema_path = "aws_rds_dbcluster/sourcedbclusteridentifier_exclusive"
