"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.conditions.Used import Used  # pylint: disable=E0401


class TestUsedConditions(BaseRuleTestCase):
    """Test template mapping configurations"""

    def setUp(self):
        """Setup"""
        super(TestUsedConditions, self).setUp()
        self.collection.register(Used())

    success_templates = [
        "test/fixtures/templates/good/generic.yaml",
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/conditions.yaml", 5)
