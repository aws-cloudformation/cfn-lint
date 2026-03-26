"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_sns_subscription
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class SubscriptionEndpointProtocol(CfnLintJsonSchema):
    id = "W3694"
    shortdesc = "SNS Subscription Endpoint should match Protocol"
    description = (
        "When an SNS Subscription Protocol is 'sqs', the Endpoint "
        "should reference an SQS Queue. When Protocol is 'lambda', "
        "the Endpoint should reference a Lambda Function."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html"
    tags = ["resources", "sns"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::SNS::Subscription/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_sns_subscription,
                filename="subscription_endpoint_protocol.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
