"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationResult, Validator
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
                "Resources/AWS::KMS::Key/Properties/KeyPolicy",
                "Resources/AWS::OpenSearchService::Domain/Properties/AccessPolicies",
                "Resources/AWS::S3::BucketPolicy/Properties/PolicyDocument",
                "Resources/AWS::SNS::TopicPolicy/Properties/PolicyDocument",
                "Resources/AWS::SQS::QueuePolicy/Properties/PolicyDocument",
            ],
            "resource",
            "policy_resource.json",
        )

    def validate(
        self,
        validator: Validator,
        policy_type: Any,
        policy: Any,
        schema: dict[str, Any],
    ) -> ValidationResult:
        for err in super().validate(validator, policy_type, policy, schema):
            if validator.context.path.cfn_path[1] == "AWS::S3::BucketPolicy":
                if err.validator == "uniqueKeys" and err.schema_path[-2] == "Statement":
                    continue
            yield err
