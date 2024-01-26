"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.custom.Operators import CreateGreaterRule  # pylint: disable=E0401


class TestGreaterOperator(BaseRuleTestCase):
    """Test template mapping configurations"""

    def setUp(self):
        """Setup"""
        super(TestGreaterOperator, self).setUp()
        self.collection.register(
            CreateGreaterRule(
                "E9001",
                "AWS::Lambda::Function",
                "Timeout",
                "50",
                "Timeout should be greater than 50",
            )
        )

    success_templates = [
        "test/fixtures/templates/good/custom/numeric-inequalities-large.yaml"
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/good/custom/numeric-inequalities-small.yaml", 2
        )
