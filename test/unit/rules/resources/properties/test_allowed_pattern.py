"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.rules.resources.properties.AllowedPattern import AllowedPattern


class TestAllowedPattern(BaseRuleTestCase):
    """Test allowed pattern Property Configuration"""

    def setUp(self):
        """Setup"""
        self.rule = AllowedPattern()

    def test_allowed_pattern(self):
        validator = Draft7Validator({"type": "string"})

        self.assertEqual(len(list(self.rule.pattern(validator, ".*", "foo", {}))), 0)
        self.assertEqual(len(list(self.rule.pattern(validator, "foo", "bar", {}))), 1)
        self.assertEqual(
            len(
                list(
                    self.rule.pattern(
                        validator, "foo", "{{resolve:ssm:S3AccessControl:2}}", {}
                    )
                )
            ),
            0,
        )
