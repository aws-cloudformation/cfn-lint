"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.resources.iam.Policy import Policy


class ResourcePolicy(Policy):
    """Check IAM resource Policies"""

    id = "E3512"
    shortdesc = "Validate resource based IAM polices"
    description = (
        "IAM resources polices are embedded JSON in CloudFormation. "
        "This rule validates those embedded policies."
    )
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html"
    tags = ["resources", "iam"]

    def __init__(self):
        super().__init__(
            [
                "AWS::KMS::Key/Properties/KeyPolicy",
                "AWS::OpenSearchService::Domain/Properties/AccessPolicies",
                "AWS::S3::BucketPolicy/Properties/PolicyDocument",
                "AWS::SNS::TopicPolicy/Properties/PolicyDocument",
                "AWS::SQS::QueuePolicy/Properties/PolicyDocument",
            ],
            "resource",
            "policy_resource.json",
        )
