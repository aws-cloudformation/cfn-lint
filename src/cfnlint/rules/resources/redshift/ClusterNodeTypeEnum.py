"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class ClusterNodeTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3667"
    shortdesc = "Validate RedShift cluster node type"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(["aws_redshift_cluster/nodetype_enum"])
