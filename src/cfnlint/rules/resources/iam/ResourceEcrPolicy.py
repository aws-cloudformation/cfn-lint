"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.iam.Policy import Policy


class ResourceEcrPolicy(Policy):
    """Check ECR repository policies"""

    id = "E3513"
    shortdesc = "Validate ECR repository policy"
    description = (
        "Private ECR repositories have a policy. " "This rule validates those policies."
    )
    source_url = "https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policies.html"
    tags = ["resources", "iam", "ecr"]

    def __init__(self):
        super().__init__("resource", "policy_resource_ecr.json")

        # remap validator to the correct function name
        self.iamresourceecrpolicy = self.validator
