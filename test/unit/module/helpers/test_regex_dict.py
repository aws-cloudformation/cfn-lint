"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.testlib.testcase import BaseTestCase

from cfnlint.helpers import RegexDict


class TestRegexDict(BaseTestCase):
    """Test Regex Dict"""

    def test_getitem(self):
        """Test success run"""

        obj = RegexDict()
        obj["^Value$"] = True

        with self.assertRaises(KeyError):
            obj["NotExist"]

    def test_get(self):
        obj = RegexDict()
        obj["^Value$"] = True

        self.assertEqual(obj.get("NotExist", "Default"), "Default")

    def test_return_longest(self):
        obj = RegexDict()
        obj["^Test"] = False
        obj["^TestLonger.*"] = True

        self.assertTrue(obj["TestLongerObject"])

    def test_contains_object(self):
        obj = RegexDict()
        obj["^Test"] = False
        obj["^TestLonger.*"] = True

        self.assertTrue("TestLongerObject" in obj)
        self.assertFalse("NotIn" in obj)
        self.assertFalse({"a": "b"} in obj)
