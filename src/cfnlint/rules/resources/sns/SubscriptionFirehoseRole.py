"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_sns_subscription
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class SubscriptionFirehoseRole(CfnLintJsonSchema):
    id = "E3728"
    shortdesc = "SNS firehose Subscription requires SubscriptionRoleArn"
    description = (
        "When an SNS Subscription Protocol is 'firehose', SubscriptionRoleArn "
        "must be specified. SNS rejects the subscription with 'Delivery protocol "
        "firehose can only be subscribed with subscription role arn'."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-sns-subscription.html#cfn-sns-subscription-subscriptionrolearn"
    tags = ["resources", "sns"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::SNS::Subscription/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_sns_subscription,
                filename="subscription_firehose_role.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return f"{err.message} when 'Protocol' is 'firehose'"
