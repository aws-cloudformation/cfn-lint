"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_dax_cluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class ClusterNodeTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3672"
    shortdesc = "Validate the cluster node type for a DAX Cluster"
    description = (
        "Validates the DAX cluster instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::DAX::Cluster/Properties/NodeType"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_dax_cluster,
                filename="nodetype_enum.json",
            ),
        )
