"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from collections import deque
from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator, ValidationError

from cfnlint.rules.resources.properties.StringSize import (
    StringSize,  # pylint: disable=E0401
)


class TestStringSize(BaseRuleTestCase):
    """Test List Size Property Configuration"""

    def test_file_positive(self):
        """Test Positive"""
        rule = StringSize()
        validator = Draft7Validator(
            {
                "type": "string",
                "maxLength": 3,
            }
        )
        self.assertEqual(list(rule.maxLength(validator, 3, "a", {})), [])
        self.assertEqual(len(list(rule.maxLength(validator, 3, "abcd", {}))), 1)
        self.assertEqual(len(list(rule.maxLength(validator, 10, {"a": "b"}, {}))), 0)
        self.assertEqual(len(list(rule.maxLength(validator, 3, {"a": "bcd"}, {}))), 1)
        self.assertEqual(
            len(list(rule.maxLength(validator, 10, {"a": {"Fn::Sub": "b"}}, {}))), 0
        )
        self.assertEqual(
            len(list(rule.maxLength(validator, 10, {"a": {"Fn::Sub": "bcd"}}, {}))), 1
        )
