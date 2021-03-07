"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.iam.Sid import Sid  # pylint: disable=E0401


class TestSid(BaseRuleTestCase):
    """Test IAM Resource Policies"""

    def setUp(self):
        """Setup"""
        super(TestSid, self).setUp()
        self.collection.register(Sid())
        self.success_templates = [
            #'test/fixtures/templates/good/resources/iam/resource_policy.yaml',
            'test/fixtures/templates/good/resources/iam/policy.yaml',
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            'test/fixtures/templates/bad/resources/iam/policy_sid.yaml', 2)
        self.helper_file_negative(
            'test/fixtures/templates/bad/resources/iam/policy_sid_2.yaml', 1)
