"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class DbClusterServerlessExclusive(CfnLintJsonSchema):
    id = "E3686"
    shortdesc = (
        "Validate when using a serverless RDS DB certain properties aren't needed"
    )
    description = (
        "When creating a serverless 'EngineMode' don't specify 'ScalingConfiguration'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(keywords=["aws_rds_dbcluster/serverless_exclusive"])

