"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.resources.iam.Policy import Policy


class ResourceSqsPolicy(Policy):
    """Check SQS queue policies"""

    id = "E3515"
    shortdesc = "Validate SQS queue policy"
    description = (
        "SQS queue policies are resource based IAM policies. "
        "This rule validates those policies, including the SQS "
        "requirement that each statement has exactly one resource."
    )
    source_url = "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-creating-custom-policies.html"
    tags = ["resources", "iam", "sqs"]

    def __init__(self):
        super().__init__(
            [
                "Resources/AWS::SQS::QueuePolicy/Properties/PolicyDocument",
            ],
            "resource",
            "policy_resource_sqs.json",
        )
