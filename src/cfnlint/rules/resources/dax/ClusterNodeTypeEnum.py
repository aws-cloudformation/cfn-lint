"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnRegionSchema import BaseCfnRegionSchema


class ClusterNodeTypeEnum(BaseCfnRegionSchema):
    id = "E3672"
    shortdesc = "Validate the cluster node type for a DAX Cluster"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]
    schema_path = "aws_dax_cluster/nodetype_enum"
