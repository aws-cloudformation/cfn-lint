"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_redshift_cluster
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class ClusterNodeTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3667"
    shortdesc = "Validate RedShift cluster node type"
    description = (
        "Validates the RedShift instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Redshift::Cluster/Properties/NodeType"],
            schema_details=SchemaDetails(
                cfnlint.data.schemas.extensions.aws_redshift_cluster,
                "nodetype_enum.json",
            ),
        )
