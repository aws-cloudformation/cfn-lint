"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from collections import deque
from test.unit.rules import BaseRuleTestCase

from cfnlint.context import Context, Value, ValueType
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.parameters.AllowedPattern import AllowedPattern
from cfnlint.template.template import Template


class TestAllowedPattern(BaseRuleTestCase):
    """Test Allowed Value Parameter Configuration"""

    def setUp(self):
        """Setup"""
        self.rule = AllowedPattern()
        cfn = Template(
            "test.yaml",
            {
                "Parameters": {
                    "1": {"Type": "String", "Default": "A"},
                    "2": {"Type": "String", "Default": 1},
                    "3": {
                        "Type": "String",
                        "AllowedValues": [
                            "A",
                            "B",
                        ],
                    },
                    "4": {
                        "Type": "String",
                        "AllowedValues": [
                            1,
                            2,
                        ],
                    },
                    "5": [],
                    "6": {"Type": "String", "AllowedValues": {"foo": "bar"}},
                    "7": {"Type": "String", "AllowedValues": [{"foo": "bar"}]},
                }
            },
            regions=["us-east-1"],
        )
        self.rule.initialize(cfn)

    def test_validate(self):
        validator = CfnTemplateValidator(
            schema={"type": "string"},
            context=Context(
                "us-east-1",
                {},
                deque(["Parameters", "MyParameter", "Default"]),
                Value(
                    "1",
                    ValueType.STANDARD,
                    deque(["Parameters", "MyParameter", "Default"]),
                ),
            ),
        )

        errs = list(self.rule.pattern(validator, "^[A-Z]$", "1", {}))
        self.assertEqual(len(errs), 1)
        for err in errs:
            self.assertEqual(err.message, "'1' does not match '^[A-Z]$'")
            self.assertEqual(err.rule, self.rule)
            self.assertEqual(
                err.path_override, deque(["Parameters", "MyParameter", "Default"])
            )
