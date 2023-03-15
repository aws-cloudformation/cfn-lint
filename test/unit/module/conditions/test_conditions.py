"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import string
from unittest import TestCase

from cfnlint.conditions import Conditions
from cfnlint.decode import decode_str
from cfnlint.template import Template


class TestConditions(TestCase):
    """Test Conditions"""

    def test_bad_condition_definition(self):
        """Badly formatted condition statements will return no results"""
        template = decode_str(
            """
        Conditions:
          IsProd: !Equals [!Ref Environment, "prod", "production"]
          IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(
            len(cfn.conditions._conditions), 1
        )  # would be 2 but IsProd fails
        # test coverage for KeyErrors in the following functions
        self.assertTrue(cfn.conditions.check_implies({"Test": True}, "IsUsEast1"))
        self.assertEqual(
            list(cfn.conditions.build_scenarios(["IsProd", "IsUsEast1"])), []
        )

    def test_run_away_scenarios(self):
        """We cap runaway scenarios"""
        template = {
            "Parameters": {},
            "Conditions": {},
        }
        condition_names = []
        for p in string.ascii_letters[0:10]:
            template["Parameters"][f"{p}Parameter"] = {
                "Type": "String",
            }
            template["Conditions"][f"{p}Condition"] = {
                "Fn::Equals": [{"Ref": f"{p}Parameter"}, "{p}"]
            }
            condition_names.append(f"{p}Condition")

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 10)
        self.assertEqual(
            len(list(cfn.conditions.build_scenarios(condition_names))),
            cfn.conditions._max_scenarios,
        )

    def test_check_implies(self):
        """We cap runaway scenarios"""
        template = {
            "Parameters": {},
            "Conditions": {},
        }
        condition_names = []
        for p in string.ascii_letters[0:4]:
            template["Parameters"][f"{p}Parameter"] = {
                "Type": "String",
            }
            template["Conditions"][f"{p}Condition"] = {
                "Fn::Equals": [{"Ref": f"{p}Parameter"}, "{p}"]
            }
            condition_names.append(f"{p}Condition")

        cfn = Template("", template)
        self.assertFalse(
            cfn.conditions.check_implies({"aCondition": False}, "aCondition")
        )
        self.assertTrue(
            cfn.conditions.check_implies({"aCondition": True}, "aCondition")
        )
        self.assertTrue(
            cfn.conditions.check_implies(
                {"aCondition": True, "bCondition": False}, "aCondition"
            )
        )
