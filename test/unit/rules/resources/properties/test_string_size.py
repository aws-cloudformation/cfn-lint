"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import datetime
from collections import deque
from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator, ValidationError

from cfnlint.rules.resources.properties.StringSize import (
    StringSize,  # pylint: disable=E0401
)


class Unserializable:
    def __init__(self) -> None:
        self.foo = "bar"


class TestStringSize(BaseRuleTestCase):
    """Test List Size Property Configuration"""

    def test_max_length(self):
        """Test max length"""
        rule = StringSize()
        validator = Draft7Validator(
            {
                "type": "string",
                "maxLength": 3,
            }
        )
        self.assertEqual(list(rule.maxLength(validator, 3, "a", {})), [])
        self.assertEqual(len(list(rule.maxLength(validator, 3, "abcd", {}))), 1)

    def test_max_object_length(self):
        """Test object max length"""
        rule = StringSize()
        validator = Draft7Validator(
            {
                "type": "object",
                "maxLength": 3,
            }
        )
        self.assertEqual(len(list(rule.maxLength(validator, 10, {"a": "b"}, {}))), 0)
        self.assertEqual(len(list(rule.maxLength(validator, 3, {"a": "bcd"}, {}))), 1)
        self.assertEqual(
            len(list(rule.maxLength(validator, 10, {"a": {"Fn::Sub": "b"}}, {}))), 0
        )
        self.assertEqual(
            len(list(rule.maxLength(validator, 3, {"Fn::Sub": "bcd"}, {}))), 1
        )
        self.assertEqual(
            len(list(rule.maxLength(validator, 3, {"Fn::Sub": ["abcd", {}]}, {}))), 1
        )
        self.assertEqual(
            len(
                list(rule.maxLength(validator, 100, {"now": datetime.date.today()}, {}))
            ),
            0,
        )
        self.assertEqual(
            len(list(rule.maxLength(validator, 100, {"now": {"Ref": "date"}}, {}))),
            0,
        )

        with self.assertRaises(TypeError):
            list(rule.maxLength(validator, 10, {"foo": Unserializable()}, {}))

    def test_min_length(self):
        """Test min length"""
        rule = StringSize()
        validator = Draft7Validator(
            {
                "type": "string",
                "minLength": 3,
            }
        )
        self.assertEqual(list(rule.minLength(validator, 3, "abcde", {})), [])
        self.assertEqual(len(list(rule.minLength(validator, 3, "ab", {}))), 1)

    def test_min_object_length(self):
        """Test min object length"""
        rule = StringSize()
        validator = Draft7Validator(
            {
                "type": "object",
                "minLength": 3,
            }
        )
        self.assertEqual(len(list(rule.minLength(validator, 5, {"a": "b"}, {}))), 0)
        self.assertEqual(len(list(rule.minLength(validator, 12, {"a": "bcd"}, {}))), 1)
        self.assertEqual(
            len(list(rule.minLength(validator, 9, {"a": {"Fn::Sub": "b"}}, {}))), 0
        )
        self.assertEqual(
            len(list(rule.minLength(validator, 6, {"Fn::Sub": "bcd"}, {}))), 1
        )
        self.assertEqual(
            len(list(rule.minLength(validator, 7, {"Fn::Sub": ["abcd", {}]}, {}))), 1
        )

        with self.assertRaises(TypeError):
            list(rule.minLength(validator, 10, {"foo": Unserializable()}, {}))

    def test_if_min(self):
        rule = StringSize()
        validator = Draft7Validator(
            {
                "type": "string",
                "maxLength": 1,
            }
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_if(
                        validator,
                        1,
                        ["Condition", "foo", "bar"],
                        {},
                        r_fn=rule.maxLength,
                    )
                )
            ),
            2,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_if(
                        validator, 1, ["Condition", 2], {}, r_fn=rule.maxLength
                    )
                )
            ),
            0,
        )
