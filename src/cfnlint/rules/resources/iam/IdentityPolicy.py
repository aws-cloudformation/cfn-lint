"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.resources.iam.Policy import Policy


class IdentityPolicy(Policy):
    """Check IAM identity Policies"""

    id = "E3510"
    shortdesc = "Validate identity based IAM polices"
    description = (
        "IAM identity polices are embedded JSON in CloudFormation. "
        "This rule validates those embedded policies."
    )
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html"
    tags = ["resources", "iam"]

    def __init__(self):
        super().__init__(
            [
                "Resources/AWS::IAM::Group/Properties/Policies/*/PolicyDocument",
                "Resources/AWS::IAM::ManagedPolicy/Properties/PolicyDocument",
                "Resources/AWS::IAM::Policy/Properties/PolicyDocument",
                "Resources/AWS::IAM::Role/Properties/Policies/*/PolicyDocument",
                "Resources/AWS::IAM::User/Properties/Policies/*/PolicyDocument",
                "Resources/AWS::SSO::PermissionSet/Properties/InlinePolicy",
            ],
            "identity",
            "policy_identity.json",
        )
