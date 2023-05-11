"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DbClusterSnapshotidentifierExclusive(BaseCfnSchema):
    id = "E3684"
    shortdesc = (
        "Validate when restoring a RDS DB from a snapshot "
        " certain properties aren't required"
    )
    description = (
        "When you specify 'SnapshotIdentifier' do not "
        "specify 'MasterUsername' or 'MasterUserPassword'"
    )
    tags = ["resources"]
    schema_path = "aws_rds_dbcluster/snapshotidentifier_exclusive"
