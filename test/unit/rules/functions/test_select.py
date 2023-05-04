"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.Select import Select  # pylint: disable=E0401


class TestRulesSelect(BaseRuleTestCase):
    """Test Rules Get Att"""

    def setUp(self):
        """Setup"""
        super(TestRulesSelect, self).setUp()
        self.collection.register(Select())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions_select.yaml", 4
        )

    def test_select_parts(self):
        rule = Select()
        # can't be a list
        self.assertEqual(len(rule._test_index_obj([], [])), 1)
        # can't be a string
        self.assertEqual(len(rule._test_index_obj("a", [])), 1)
        # can be a valid fn
        self.assertEqual(len(rule._test_index_obj({"Ref": "Test"}, [])), 0)
        # can't be an invalid fn
        self.assertEqual(len(rule._test_index_obj({"Foo": "Bar"}, [])), 1)
        # can't be a dict of many values
        self.assertEqual(
            len(rule._test_index_obj({"Ref": "Test", "Foo": "Bar"}, [])), 1
        )

        self.assertEqual(len(rule._test_index_obj({}, [])), 1)

        # supported function
        self.assertEqual(len(rule._test_list_obj({"Ref": "Test"}, [])), 0)
        # Unsupported function
        self.assertEqual(len(rule._test_list_obj({"Foo": "Bar"}, [])), 1)
        # Unsupported type
        self.assertEqual(len(rule._test_list_obj("foo", [])), 1)
