"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.parameters.AllowedPattern import (  # pylint: disable=E0401
    AllowedPattern,
)
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
        self.assertEqual(len(list(self.rule.validate("1", "^[A-Z]$"))), 0)
        self.assertEqual(len(list(self.rule.validate("1", "^[1-9]$"))), 1)
        self.assertEqual(len(list(self.rule.validate("2", "^[1-9]$"))), 0)
        self.assertEqual(len(list(self.rule.validate("2", "^[A-Z]$"))), 1)
        # allowed values
        self.assertEqual(len(list(self.rule.validate("3", "^[A-Z]$"))), 0)
        self.assertEqual(len(list(self.rule.validate("3", "^[1-9]$"))), 2)
        self.assertEqual(len(list(self.rule.validate("4", "^[1-9]$"))), 0)
        self.assertEqual(len(list(self.rule.validate("4", "^[A-Z]$"))), 2)

        # bad structure on parameter
        self.assertEqual(len(list(self.rule.validate("5", "^[A-Z]$"))), 0)
        self.assertEqual(len(list(self.rule.validate("6", "^[A-Z]$"))), 0)
        self.assertEqual(len(list(self.rule.validate("7", "^[A-Z]$"))), 0)
