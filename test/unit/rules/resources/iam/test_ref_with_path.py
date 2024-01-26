"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.iam.RefWithPath import RefWithPath  # pylint: disable=E0401


class TestRefWithPath(BaseRuleTestCase):
    """Test IAM Policies"""

    def setUp(self):
        """Setup"""
        super(TestRefWithPath, self).setUp()
        self.collection.register(RefWithPath())
        self.success_templates = [
            "test/fixtures/templates/good/resources/iam/ref_with_path.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/iam/ref_with_path.yaml", 1
        )
