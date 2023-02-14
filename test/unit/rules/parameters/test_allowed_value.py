"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.parameters.AllowedValue import AllowedValue  # pylint: disable=E0401
from cfnlint.template.template import Template


class TestAllowedValue(BaseRuleTestCase):
    """Test Allowed Value Parameter Configuration"""

    def setUp(self):
        """Setup"""
        self.rule = AllowedValue()
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
                    "6:": {"Type": "String", "AllowedValues": {"foo": "bar"}},
                }
            },
            regions=["us-east-1"],
        )
        self.rule.initialize(cfn)

    def test_validate(self):
        self.assertEqual(len(list(self.rule.validate("1", ["A", "B"]))), 0)
        self.assertEqual(len(list(self.rule.validate("1", ["B", "C"]))), 1)
        self.assertEqual(len(list(self.rule.validate("2", [1, 2]))), 0)
        self.assertEqual(len(list(self.rule.validate("2", [2, 3]))), 1)
        # allowed values
        self.assertEqual(len(list(self.rule.validate("3", ["A", "B"]))), 0)
        self.assertEqual(len(list(self.rule.validate("3", ["B", "C"]))), 1)
        self.assertEqual(len(list(self.rule.validate("4", [1, 2]))), 0)
        self.assertEqual(len(list(self.rule.validate("4", [2, 3]))), 1)

        # bad structure on parameter
        self.assertEqual(len(list(self.rule.validate("5", ["foo"]))), 0)
        self.assertEqual(len(list(self.rule.validate("6", ["foo"]))), 0)
