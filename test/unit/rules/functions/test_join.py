"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.Join import Join  # pylint: disable=E0401


class TestRulesJoin(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesJoin, self).setUp()
        self.collection.register(Join())
        self.success_templates = [
            "test/fixtures/templates/good/functions/join.yaml",
        ]

    def test_functions(self):
        """Test some of the base functions"""
        rule = Join()

        output = rule._normalize_getatt("Resource.Output")
        self.assertEqual(output[0], "Resource")
        self.assertEqual(output[1], "Output")

        output = rule._normalize_getatt("Resource.Outputs.Output")
        self.assertEqual(output[0], "Resource")
        self.assertEqual(output[1], "Outputs.Output")

        output = rule._normalize_getatt(["Resource", "Output"])
        self.assertEqual(output[0], "Resource")
        self.assertEqual(output[1], "Output")

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/functions/join.yaml", 11)
