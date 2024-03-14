"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.resources.iam.ResourceEcrPolicy import ResourceEcrPolicy


class TestResourceEcrPolicy(TestCase):
    """Test IAM identity Policies"""

    def setUp(self):
        """Setup"""
        self.rule = ResourceEcrPolicy()

    def test_string_statements(self):
        """Test Positive"""
        validator = CfnTemplateValidator()

        # no resource statement
        # ruff: noqa: E501
        policy = """
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowCrossAccountPush",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": "arn:aws:iam::123456789012:root"
                        },
                        "Action": [
                            "ecr:BatchCheckLayerAvailability",
                            "ecr:CompleteLayerUpload",
                            "ecr:InitiateLayerUpload",
                            "ecr:PutImage",
                            "ecr:UploadLayerPart"
                        ]
                    }
                ]
            }
        """

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 0, errs)
