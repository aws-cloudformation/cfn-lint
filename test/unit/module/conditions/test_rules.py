"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

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
          Rule:
            Assertions:
            - Assert:
                Fn::And:
                - !Condition IsProd
                - !Condition IsUsEast1

        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertEqual(len(cfn.conditions._rules), 1)

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
            RuleCondition: !Condition IsProd
            Assertions:
            - Assert: !Condition IsUsEast1
          Rule2:
            RuleCondition: !Condition IsDev
            Assertions:
            - Assert: !Condition IsNotUsEast1
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 4)
        self.assertEqual(len(cfn.conditions._rules), 2)

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
