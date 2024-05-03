"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_emr_cluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class ClusterInstanceTypeConfigInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3675"
    shortdesc = "Validate EMR cluster instance type"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "AWS::EMR::Cluster/Properties/CoreInstanceFleet/InstanceTypeConfigs/InstanceType",
                "AWS::EMR::Cluster/Properties/TaskInstanceFleets/InstanceTypeConfigs/InstanceType",
                "AWS::EMR::Cluster/Properties/CoreInstanceGroup/InstanceType",
                "AWS::EMR::Cluster/Properties/TaskInstanceGroups/InstanceType",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_emr_cluster,
                filename="instancetypeconfig_instancetype_enum.json",
            ),
        )
