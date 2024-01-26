"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.custom.Operators import CreateCustomIsDefinedRule


class TestIsDefinedRule(BaseRuleTestCase):
    """Test template mapping configurations"""

    def setUp(self):
        """Setup"""
        super(TestIsDefinedRule, self).setUp()
        self.collection.register(
            CreateCustomIsDefinedRule(
                "E9001",
                "AWS::Lambda::Function",
                "Environment.Variables.NODE_ENV",
                "NOT_DEFINED",
                "NODE_ENV should not be defined",
            )
        )

    success_templates = ["test/fixtures/templates/good/custom/is-not-defined.yaml"]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/good/custom/is-defined.yaml", 6
        )
