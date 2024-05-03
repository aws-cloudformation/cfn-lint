"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator

# ruff: noqa: E501
from cfnlint.rules.resources.properties.Type import Type


class TestType(BaseRuleTestCase):
    """Test Primitive Value Types for Json Schema non strict"""

    def setUp(self):
        """Setup"""
        self.rule = Type()
        self.rule.config["strict"] = False
        self.validator = CfnTemplateValidator()

    def check_args(self, types, instance, extra_args):
        errs = list(self.rule.type(self.validator, types, instance, {}))
        self.assertEqual(len(errs), 1)
        self.assertDictEqual(
            errs[0].extra_args,
            extra_args,
        )

    def test_validation_non_strict(self):
        self.rule.config["strict"] = False
        # sub is a string boolean
        self.check_args(
            types="integer",
            instance="A",
            extra_args={
                "actual_type": "string",
                "expected_type": "integer",
            },
        )
        self.check_args(
            types=["number", "integer"],
            instance="A",
            extra_args={
                "actual_type": "string",
                "expected_type": "number",
            },
        )

    def test_validation_strict(self):
        self.rule.config["strict"] = True
        # sub is a string boolean
        self.check_args(
            types="integer",
            instance="1",
            extra_args={
                "actual_type": "string",
                "expected_type": "integer",
            },
        )
        self.check_args(
            types=["string", "boolean"],
            instance=1,
            extra_args={
                "actual_type": "integer",
                "expected_type": "string",
            },
        )
