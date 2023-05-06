"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.rules.resources.properties.ListSize import (
    ListSize,  # pylint: disable=E0401
)


class TestListSize(BaseRuleTestCase):
    """Test List Size Property Configuration"""

    def test_list_size_max(self):
        """Test maximum"""
        rule = ListSize()
        validator = Draft7Validator({"type": "array", "maxItems": 1})
        self.assertEqual(list(rule.maxItems(validator, 1, ["foo"], {})), [])
        self.assertEqual(len(list(rule.maxItems(validator, 1, ["foo", "bar"], {}))), 1)

    def test_list_size_min(self):
        """Test minimum"""
        rule = ListSize()
        validator = Draft7Validator(
            {
                "type": "array",
                "minItems": 2,
            }
        )
        self.assertEqual(list(rule.minItems(validator, 2, ["foo", "bar"], {})), [])
        self.assertEqual(len(list(rule.minItems(validator, 2, ["foo"], {}))), 1)

    def test_list_if(self):
        """Test if"""
        rule = ListSize()
        validator = Draft7Validator(
            {
                "type": "array",
                "minItems": 2,
            }
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_if(
                        validator, 2, ["Condition", [0], [1]], {}, r_fn=rule.minItems
                    )
                )
            ),
            2,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_if(
                        validator, 1, ["Condition", 2], {}, r_fn=rule.minItems
                    )
                )
            ),
            0,
        )
