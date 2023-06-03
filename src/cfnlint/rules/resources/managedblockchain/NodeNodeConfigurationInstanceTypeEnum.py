"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class NodeNodeConfigurationInstanceTypeEnum(BaseCfnRegionSchema):
    id = "E3617"
    shortdesc = "Validate ManagedBlockchain instance type"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = "aws_managedblockchain_node/nodeconfiguration_instancetype_enum"
