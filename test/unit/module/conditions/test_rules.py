"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

from cfnlint.conditions._rule import _Assertion
from cfnlint.decode import decode_str
from cfnlint.template import Template


class TestConditionsWithRules(TestCase):

    def test_conditions_with_rules(self):
        template = decode_str(
            """
        Conditions:
          IsProd: !Equals [!Ref Environment, "prod"]
          IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]
        Rules:
          Rule1:
            Assertions:
            - Assert:
                Fn::And:
                - !Condition IsProd
                - !Condition IsUsEast1
          Rule2:
            Assertions:
            - Assert:
                Fn::Or:
                - !Condition IsProd
                - !Condition IsUsEast1
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertEqual(len(cfn.conditions._rules), 2)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "d0f5e92fc5233a6b011342df171f191838491056",
                "362a2ca660fa34c91feeee4681e8433101d2a687",
            ],
        )

        self.assertTrue(
            cfn.conditions.satisfiable(
                {"IsProd": True, "IsUsEast1": True},
                {"AWS::Region": "us-east-1", "Environment": "prod"},
            )
        )
        self.assertFalse(
            cfn.conditions.satisfiable(
                {"IsProd": True, "IsUsEast1": False},
                {"AWS::Region": "us-west-2", "Environment": "prod"},
            )
        )
        self.assertFalse(
            cfn.conditions.satisfiable(
                {"IsProd": False, "IsUsEast1": True},
                {"AWS::Region": "us-east-1", "Environment": "dev"},
            )
        )
        self.assertFalse(
            cfn.conditions.satisfiable(
                {"IsProd": False, "IsUsEast1": False},
                {"AWS::Region": "us-west-2", "Environment": "dev"},
            )
        )

    def test_conditions_with_rules_implies(self):
        template = decode_str(
            """
        Conditions:
          IsProd: !Equals [!Ref Environment, "prod"]
          IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]
        Rules:
          Rule:
            RuleCondition: !Condition IsProd
            Assertions:
            - Assert: !Condition IsUsEast1

        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertEqual(len(cfn.conditions._rules), 1)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "d0f5e92fc5233a6b011342df171f191838491056",
                "362a2ca660fa34c91feeee4681e8433101d2a687",
            ],
        )

        self.assertTrue(
            cfn.conditions.satisfiable(
                {"IsProd": True, "IsUsEast1": True},
                {"AWS::Region": "us-east-1", "Environment": "prod"},
            )
        )
        self.assertFalse(
            cfn.conditions.satisfiable(
                {"IsProd": True, "IsUsEast1": False},
                {"AWS::Region": "us-west-2", "Environment": "prod"},
            )
        )
        self.assertTrue(
            cfn.conditions.satisfiable(
                {"IsProd": False, "IsUsEast1": True},
                {"AWS::Region": "us-east-1", "Environment": "dev"},
            )
        )
        self.assertTrue(
            cfn.conditions.satisfiable(
                {"IsProd": False, "IsUsEast1": False},
                {"AWS::Region": "us-west-2", "Environment": "dev"},
            )
        )

    def test_conditions_with_multiple_rules(self):
        template = decode_str(
            """
        Parameters:
          Environment:
            Type: String
            Default: dev
            AllowedValues:
            - dev
            - stage
            - prod
        Conditions:
          IsProd: !Equals [!Ref Environment, "prod"]
          IsDev: !Equals [!Ref Environment, "dev"]
          IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]
          IsNotUsEast1: !Not [!Condition IsUsEast1]
        Rules:
          Rule1:
            RuleCondition: !Equals [!Ref Environment, "prod"]
            Assertions:
            - Assert: !Condition IsUsEast1
          Rule2:
            RuleCondition: !Equals [!Ref Environment, "dev"]
            Assertions:
            - Assert: !Not [!Condition IsUsEast1]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 4)
        self.assertEqual(len(cfn.conditions._rules), 2)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "d0f5e92fc5233a6b011342df171f191838491056",
                "362a2ca660fa34c91feeee4681e8433101d2a687",
            ],
        )
        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[1].equals],
            [
                "d2dab653475dd270354fe84c4f80b54883e958bb",
                "362a2ca660fa34c91feeee4681e8433101d2a687",
            ],
        )

        self.assertTrue(
            cfn.conditions.satisfiable(
                {
                    "IsProd": True,
                    "IsUsEast1": True,
                    "IsDev": False,
                    "IsNotUsEast1": False,
                },
                {"AWS::Region": "us-east-1", "Environment": "prod"},
            )
        )
        self.assertFalse(
            cfn.conditions.satisfiable(
                {
                    "IsProd": True,
                    "IsUsEast1": False,
                    "IsDev": False,
                    "IsNotUsEast1": False,
                },
                {"AWS::Region": "us-west-2", "Environment": "prod"},
            )
        )
        self.assertFalse(
            cfn.conditions.satisfiable(
                {
                    "IsProd": False,
                    "IsUsEast1": True,
                    "IsDev": True,
                    "IsNotUsEast1": False,
                },
                {"AWS::Region": "us-east-1", "Environment": "dev"},
            )
        )
        self.assertTrue(
            cfn.conditions.satisfiable(
                {
                    "IsProd": False,
                    "IsUsEast1": False,
                    "IsDev": True,
                    "IsNotUsEast1": True,
                },
                {"AWS::Region": "us-west-2", "Environment": "dev"},
            )
        )
        self.assertTrue(
            cfn.conditions.satisfiable(
                {
                    "IsProd": False,
                    "IsUsEast1": True,
                    "IsDev": False,
                    "IsNotUsEast1": False,
                },
                {"AWS::Region": "us-east-1", "Environment": "stage"},
            )
        )
        self.assertTrue(
            cfn.conditions.satisfiable(
                {
                    "IsProd": False,
                    "IsUsEast1": False,
                    "IsDev": False,
                    "IsNotUsEast1": True,
                },
                {"AWS::Region": "us-west-2", "Environment": "stage"},
            )
        )


class TestAssertion(TestCase):
    def test_assertion_errors(self):
        with self.assertRaises(ValueError):
            _Assertion({"A": "B", "C": "D"}, {})

        with self.assertRaises(ValueError):
            _Assertion({"Fn::Not": {"C": "D"}}, {})

        with self.assertRaises(ValueError):
            _Assertion({"Not": {"C": "D"}}, {})

        with self.assertRaises(ValueError):
            _Assertion({"Condition": {"C": "D"}}, {})

    def test_init_rules_with_list(self):
        template = decode_str(
            """
        Conditions:
          IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]
          IsNotUsEast1: !Not [!Condition IsUsEast1]
        Rules: []
        """
        )[0]

        cfn = Template("", template)
        self.assertListEqual(cfn.conditions._rules, [])

    def test_init_rules_with_wrong_assertions_type(self):
        template = decode_str(
            """
        Conditions:
          IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]
          IsNotUsEast1: !Not [!Condition IsUsEast1]
        Rules:
          Rule1:
            Assertions: {"Foo": "Bar"}
          Rule2:
            Assertions:
            - Assert: !Condition IsUsEast1
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._rules), 1)

    def test_init_rules_with_no_keys(self):
        template = decode_str(
            """
        Conditions:
          IsUsEast1: !Equals [!Ref "AWS::Region", "us-east-1"]
          IsNotUsEast1: !Not [!Condition IsUsEast1]
        Rules:
          Rule1:
            Foo: Bar
          Rule2:
            Assertions:
            - Assert:
                Fn::Or:
                - !Condition IsNotUsEast1
                - !Condition IsUsEast1
          Rule3: []
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._rules), 1)
