"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbcluster
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbClusterMonitoring(CfnLintJsonSchema):
    id = "E3689"
    shortdesc = "Validate MonitoringInterval and MonitoringRoleArn are used together"
    description = (
        "When MonitoringInterval is greater than 0 you need to specify "
        "MonitoringRoleArn. If MonitoringRoleArn is specified "
        "MonitoringInterval has to be greather than 0."
    )
    tags = ["resources"]
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-monitoringinterval"

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBCluster/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbcluster,
                filename="monitoring.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "You must have 'MonitoringRoleArn' specified with "
            "'MonitoringInterval' greater than 0"
        )
