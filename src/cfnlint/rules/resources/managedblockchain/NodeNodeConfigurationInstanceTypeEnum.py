"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class NodeNodeConfigurationInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3617"
    shortdesc = "Validate ManagedBlockchain instance type"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(["aws_managedblockchain_node/nodeconfiguration_instancetype_enum"])
