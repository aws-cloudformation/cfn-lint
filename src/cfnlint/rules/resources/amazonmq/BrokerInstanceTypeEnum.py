"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class BrokerInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3670"
    shortdesc = "Validate the instance types for an AmazonMQ Broker"
    description = (
        "Validates the instance types based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(["aws_amazonmq_broker/instancetype_enum"])
