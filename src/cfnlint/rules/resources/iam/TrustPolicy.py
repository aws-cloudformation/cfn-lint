"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.resources.iam.Policy import Policy


class TrustPolicy(Policy):
    """Check IAM trust Policies"""

    id = "E3530"
    shortdesc = "Validate IAM trust polices"
    description = (
        "IAM trust polices are embedded JSON in CloudFormation. "
        "This rule validates those embedded policies."
    )
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html"
    tags = ["resources", "iam"]

    def __init__(self):
        super().__init__(
            [
                "Resources/AWS::IAM::Role/Properties/AssumeRolePolicyDocument",
            ],
            "trust",
            "policy_trust.json",
        )
