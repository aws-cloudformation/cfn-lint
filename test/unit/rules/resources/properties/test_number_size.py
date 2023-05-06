"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.rules.resources.properties.NumberSize import (
    NumberSize,  # pylint: disable=E0401
)


class TestNumberSize(BaseRuleTestCase):
    """Test Number Size Property Configuration"""

    def test_number_size_max(self):
        """Test maximum"""
        rule = NumberSize()
        validator = Draft7Validator(
            {
                "type": "integer",
                "maximum": 1,
            }
        )
        self.assertEqual(list(rule.maximum(validator, 1, 1, {})), [])
        self.assertEqual(list(rule.maximum(validator, 1, "1", {})), [])
        self.assertEqual(len(list(rule.maximum(validator, 1, 2, {}))), 1)
        self.assertEqual(len(list(rule.maximum(validator, 1, "2", {}))), 1)

    def test_number_size_min(self):
        """Test minimum"""
        rule = NumberSize()
        validator = Draft7Validator(
            {
                "type": "integer",
                "maximum": 1,
            }
        )
        self.assertEqual(list(rule.minimum(validator, 1, 1, {})), [])
        self.assertEqual(list(rule.minimum(validator, 1, "1", {})), [])
        self.assertEqual(len(list(rule.minimum(validator, 1, 0, {}))), 1)
        self.assertEqual(len(list(rule.minimum(validator, 1, "0", {}))), 1)

    def test_number_size_exclusive_max(self):
        """Test exlusive maximum"""
        rule = NumberSize()
        validator = Draft7Validator(
            {
                "type": "integer",
                "maximum": 1,
            }
        )
        self.assertEqual(list(rule.exclusiveMaximum(validator, 1, 0, {})), [])
        self.assertEqual(list(rule.exclusiveMaximum(validator, 1, "0", {})), [])
        self.assertEqual(len(list(rule.exclusiveMaximum(validator, 1, 2, {}))), 1)
        self.assertEqual(len(list(rule.exclusiveMaximum(validator, 1, "2", {}))), 1)

    def test_number_size_exclusive_min(self):
        """Test exlusive minimum"""
        rule = NumberSize()
        validator = Draft7Validator(
            {
                "type": "integer",
                "maximum": 1,
            }
        )
        self.assertEqual(list(rule.exclusiveMinimum(validator, 1, 2, {})), [])
        self.assertEqual(list(rule.exclusiveMinimum(validator, 1, "2", {})), [])
        self.assertEqual(len(list(rule.exclusiveMinimum(validator, 1, 0, {}))), 1)
        self.assertEqual(len(list(rule.exclusiveMinimum(validator, 1, "0", {}))), 1)

    def test_if_min(self):
        rule = NumberSize()
        validator = Draft7Validator(
            {
                "type": "integer",
                "maximum": 1,
            }
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_if(
                        validator, 1, ["Condition", 2, 3], {}, r_fn=rule.maximum
                    )
                )
            ),
            2,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_if(
                        validator, 1, ["Condition", 2], {}, r_fn=rule.maximum
                    )
                )
            ),
            0,
        )
