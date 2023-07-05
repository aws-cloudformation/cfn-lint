"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.Split import Split  # pylint: disable=E0401


class TestRulesSplit(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesSplit, self).setUp()
        self.collection.register(Split())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/functions_split.yaml", 4)

    def test_split_parts(self):
        rule = Split()
        self.assertEqual(len(rule._test_delimiter({}, [])), 1)
        self.assertEqual(len(rule._test_string({}, [])), 1)

        # supported function
        self.assertEqual(len(rule._test_string({"Ref": "Test"}, [])), 0)
        # Unsupported function
        self.assertEqual(len(rule._test_string({"Foo": "Bar"}, [])), 1)
