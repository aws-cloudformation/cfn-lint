"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

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
        super().__init__(["aws_emr_cluster/instancetypeconfig_instancetype_enum"])
