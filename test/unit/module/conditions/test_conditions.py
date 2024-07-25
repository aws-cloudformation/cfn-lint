"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import string
from unittest import TestCase

from cfnlint.conditions import UnknownSatisfisfaction
from cfnlint.conditions._utils import get_hash
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
        self.assertTrue(
            cfn.conditions.check_implies(
                {
                    "Test": True,
                },
                "IsUsEast1",
            )
        )
        self.assertEqual(
            list(cfn.conditions.build_scenarios({"IsProd": None, "IsUsEast1": None})),
            [],
        )

    def test_run_away_scenarios(self):
        """We cap runaway scenarios"""
        template = {
            "Parameters": {},
            "Conditions": {},
        }
        condition_names = {}
        for p in string.ascii_letters[0:10]:
            template["Parameters"][f"{p}Parameter"] = {
                "Type": "String",
            }
            template["Conditions"][f"{p}Condition"] = {
                "Fn::Equals": [{"Ref": f"{p}Parameter"}, "{p}"]
            }
            condition_names[f"{p}Condition"] = None

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 10)
        self.assertEqual(
            len(list(cfn.conditions.build_scenarios(condition_names))),
            cfn.conditions._max_scenarios,
        )

    def test_check_implies(self):
        """We properly validate implies scenarios"""
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

    def test_check_always_true_or_false(self):
        """We properly validate static equals"""
        template = decode_str(
            """
        Parameters:
          FalseParameter:
            Default: "false"
            Type: String
        Conditions:
          IsTrue: !Equals ["true", "true"]
          IsFalse: !Equals [!Ref FalseParameter, !Ref FalseParameter]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        # test coverage for KeyErrors in the following functions
        self.assertTrue(cfn.conditions.check_implies({"IsTrue": True}, "IsFalse"))

    def test_check_never_false(self):
        """With allowed values two conditions can not both be false"""
        template = decode_str(
            """
        Parameters:
          Environment:
            Type: String
            AllowedValues: ["prod", "dev"]
        Conditions:
          IsProd: !Equals [!Ref Environment, "prod"]
          IsDev: !Equals [!Ref Environment, "dev"]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertListEqual(
            list(cfn.conditions.build_scenarios({"IsProd": None, "IsDev": None})),
            [
                {"IsProd": True, "IsDev": False},
                {"IsProd": False, "IsDev": True},
            ],
        )

    def test_check_can_be_false(self):
        """With allowed values two conditions can both be false"""
        template = decode_str(
            """
        Parameters:
          Environment:
            Type: String
            AllowedValues: ["prod", "dev", "stage"]
        Conditions:
          IsProd: !Equals [!Ref Environment, "prod"]
          IsDev: !Equals [!Ref Environment, "dev"]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertListEqual(
            list(cfn.conditions.build_scenarios({"IsProd": None, "IsDev": None})),
            [
                {"IsProd": True, "IsDev": False},
                {"IsProd": False, "IsDev": True},
                {"IsProd": False, "IsDev": False},
            ],
        )
        self.assertListEqual(
            list(cfn.conditions.build_scenarios({"IsProd": {True}, "IsDev": None})),
            [
                {"IsProd": True, "IsDev": False},
            ],
        )
        self.assertListEqual(
            list(cfn.conditions.build_scenarios({"IsProd": {False}, "IsDev": None})),
            [
                {"IsProd": False, "IsDev": True},
                {"IsProd": False, "IsDev": False},
            ],
        )

    def test_check_can_be_good_when_condition_value(self):
        """Some times a condition Equals doesn't match to allowed values"""
        template = decode_str(
            """
        Parameters:
          Environment:
            Type: String
            AllowedValues: ["prod", "dev", "stage"]
        Conditions:
          IsGamma: !Equals [!Ref Environment, "gamma"]
          IsBeta: !Equals ["beta", !Ref Environment]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertListEqual(
            list(cfn.conditions.build_scenarios({"IsGamma": None, "IsBeta": None})),
            [
                {"IsBeta": False, "IsGamma": False},
            ],
        )
        self.assertListEqual(
            list(cfn.conditions.build_scenarios({"IsGamma": None})),
            [
                {"IsGamma": False},
            ],
        )

    def test_check_condition_region(self):
        """Regional based condition testing"""
        template = decode_str(
            """
        Parameters:
          Environment:
            Type: String
            AllowedValues: ["prod", "dev", "stage"]
        Conditions:
          IsUsEast1: !Equals [!Ref AWS::Region, "us-east-1"]
          IsUsWest2: !Equals ["us-west-2", !Ref AWS::Region]
          IsProd: !Equals [!Ref Environment, "prod"]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 3)
        self.assertListEqual(
            cfn.conditions.build_scenerios_on_region("IsUsEast1", "us-east-1"),
            [
                True,
            ],
        )
        self.assertListEqual(
            cfn.conditions.build_scenerios_on_region("IsUsEast1", "us-west-2"),
            [
                False,
            ],
        )
        self.assertListEqual(
            cfn.conditions.build_scenerios_on_region("IsUsWest2", "us-west-2"),
            [
                True,
            ],
        )
        self.assertListEqual(
            cfn.conditions.build_scenerios_on_region("IsUsWest2", "us-east-1"),
            [
                False,
            ],
        )
        self.assertListEqual(
            cfn.conditions.build_scenerios_on_region("IsProd", "us-east-1"),
            [
                True,
                False,
            ],
        )
        self.assertListEqual(
            cfn.conditions.build_scenerios_on_region("Foo", "us-east-1"),
            [
                True,
                False,
            ],
        )

    def test_test_condition(self):
        """Get condition and test"""
        template = decode_str(
            """
        Parameters:
          Environment:
            Type: String
            AllowedValues: ["prod", "dev", "stage"]
        Conditions:
          IsUsEast1: !Equals [!Ref AWS::Region, "us-east-1"]
          IsUsWest2: !Equals ["us-west-2", !Ref AWS::Region]
          IsProd: !Equals [!Ref Environment, "prod"]
          IsUsEast1AndProd: !And [!Condition IsUsEast1, !Condition IsProd]
        """
        )[0]

        h_region = get_hash({"Ref": "AWS::Region"})
        h_environment = get_hash({"Ref": "Environment"})

        cfn = Template("", template)
        self.assertTrue(cfn.conditions.get("IsUsEast1").test({h_region: "us-east-1"}))
        self.assertFalse(cfn.conditions.get("IsProd").test({h_environment: "dev"}))
        self.assertTrue(
            cfn.conditions.get("IsUsEast1AndProd").test(
                {h_region: "us-east-1", h_environment: "prod"}
            )
        )
        self.assertFalse(
            cfn.conditions.get("IsUsEast1AndProd").test(
                {h_region: "us-east-1", h_environment: "dev"}
            )
        )

    def test_build_scenerios_on_region_with_condition_dne(self):
        """Get condition and test"""
        template = decode_str(
            """
        Conditions:
          IsUsEast1: !Equals [!Ref AWS::Region, "us-east-1"]
        """
        )[0]

        cfn = Template("", template)
        self.assertListEqual(
            list(cfn.conditions.build_scenerios_on_region("IsProd", "us-east-1")),
            [True, False],
        )

    def test_satifaction(self):
        """Get condition and test"""
        template = decode_str(
            """
        Parameters:
          SecurityGroups:
            Default: ""
            Type: CommaDelimitedList
        Conditions:
          IsUsEast1: !Equals [!Ref AWS::Region, "us-east-1"]
          HasSecurityGroups: !Not [ !Equals [ !Join [ '', !Ref SecurityGroups ], ''] ]
        """
        )[0]

        cfn = Template("", template)

        with self.assertRaises(UnknownSatisfisfaction):
            cfn.conditions.satisfiable(
                {"HasSecurityGroups": True}, {"SecurityGroups": [""]}
            )
