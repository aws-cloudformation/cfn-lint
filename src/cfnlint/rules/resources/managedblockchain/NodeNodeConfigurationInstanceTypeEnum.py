"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_managedblockchain_node
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class NodeNodeConfigurationInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3617"
    shortdesc = "Validate ManagedBlockchain instance type"
    description = (
        "Validates the ManagedBlockchain instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ManagedBlockchain::Node/Properties/NodeConfiguration/InstanceType"
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_managedblockchain_node,
                filename="nodeconfiguration_instancetype_enum.json",
            ),
        )
