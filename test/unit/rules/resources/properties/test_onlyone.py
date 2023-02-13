"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.rules.resources.properties.OnlyOne import OnlyOne  # pylint: disable=E0401


class TestPropertyOnlyOne(BaseRuleTestCase):
    """Test OnlyOne Property Configuration"""

    def test_allowed_value(self):
        """Test Positive"""
        rule = OnlyOne()
        schemas = [
            {"type": "string", "enum": ["a", "b"]},
            {"type": "string", "enum": ["b", "c"]},
        ]
        validator = Draft7Validator({})
        self.assertEqual(len(list(rule.oneOf(validator, schemas, "a", {}))), 0)
        self.assertEqual(len(list(rule.oneOf(validator, schemas, "b", {}))), 1)
        self.assertEqual(len(list(rule.oneOf(validator, schemas, "d", {}))), 1)
