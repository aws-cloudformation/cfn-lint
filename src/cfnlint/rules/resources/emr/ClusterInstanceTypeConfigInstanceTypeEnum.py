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
        "Validates the EMR cluster instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EMR::Cluster/Properties/Instances/CoreInstanceFleet/InstanceTypeConfigs/*/InstanceType",
                "Resources/AWS::EMR::Cluster/Properties/Instances/CoreInstanceGroup/InstanceType",
                "Resources/AWS::EMR::Cluster/Properties/Instances/TaskInstanceFleets/*/InstanceTypeConfigs/*/InstanceType",
                "Resources/AWS::EMR::Cluster/Properties/Instances/TaskInstanceGroups/*/InstanceType",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_emr_cluster,
                filename="instancetypeconfig_instancetype_enum.json",
            ),
        )
