"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class InstanceInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3628"
    shortdesc = "Validate instance types based on region"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(["aws_ec2_instance/instancetype_enum"])
