"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class DbClusterServerlessExclusive(BaseCfnSchema):
    id = "E3686"
    shortdesc = (
        "Validate when using a serverless RDS DB certain properties aren't needed"
    )
    description = (
        "When creating a serverless 'EngineMode' don't specify 'ScalingConfiguration'"
    )
    tags = ["resources"]
    schema_path = "aws_rds_dbcluster/serverless_exclusive"
