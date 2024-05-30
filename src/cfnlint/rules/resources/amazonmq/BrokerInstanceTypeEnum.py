"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_amazonmq_broker
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class BrokerInstanceTypeEnum(CfnLintJsonSchemaRegional):
    id = "E3670"
    shortdesc = "Validate the instance types for an AmazonMQ Broker"
    description = (
        "Validates the instance types for AmazonMQ broker based on region "
        "and data gathered from the pricing APIs"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::AmazonMQ::Broker/Properties/HostInstanceType"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_amazonmq_broker,
                filename="instancetype_enum.json",
            ),
        )
