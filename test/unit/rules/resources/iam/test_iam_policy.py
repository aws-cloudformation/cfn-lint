"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.iam.Policy import Policy  # pylint: disable=E0401


class TestPropertyIamPolicies(BaseRuleTestCase):
    """Test IAM Policies"""

    def setUp(self):
        """Setup"""
        super(TestPropertyIamPolicies, self).setUp()
        self.collection.register(Policy())
        self.success_templates = [
            "test/fixtures/templates/good/resources/iam/policy.yaml",
            "test/fixtures/templates/good/resources/iam/resource_policy.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/iam/iam_policy.yaml", 12
        )

    def test_file_resource_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/iam/resource_policy.yaml", 4
        )
