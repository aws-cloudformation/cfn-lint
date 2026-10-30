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
                - !Equals [!Ref Environment, "prod"]
                - !Equals [!Ref "AWS::Region", "us-east-1"]
          Rule2:
            Assertions:
            - Assert:
                Fn::Or:
                - !Equals [!Ref Environment, "prod"]
                - !Equals [!Ref "AWS::Region", "us-east-1"]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertEqual(len(cfn.conditions._rules), 2)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "b35dea1a59b5e61fc42036a0100a5c4f906c1d09",
                "f8640cf81907d2a1c75433d951c9f0d4bbb25b60",
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
            RuleCondition: !Equals [!Ref Environment, "prod"]
            Assertions:
            - Assert: !Equals [!Ref "AWS::Region", "us-east-1"]

        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertEqual(len(cfn.conditions._rules), 1)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "b35dea1a59b5e61fc42036a0100a5c4f906c1d09",
                "f8640cf81907d2a1c75433d951c9f0d4bbb25b60",
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
            - Assert: !Equals [!Ref "AWS::Region", "us-east-1"]
          Rule2:
            RuleCondition: !Equals [!Ref Environment, "dev"]
            Assertions:
            - Assert: !Not [!Equals [!Ref "AWS::Region", "us-east-1"]]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 4)
        self.assertEqual(len(cfn.conditions._rules), 2)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "b35dea1a59b5e61fc42036a0100a5c4f906c1d09",
                "f8640cf81907d2a1c75433d951c9f0d4bbb25b60",
            ],
        )
        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[1].equals],
            [
                "227dcb1c5c68059b461d105f3ef724b760870a6d",
                "f8640cf81907d2a1c75433d951c9f0d4bbb25b60",
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

    def test_fn_equals_assertions_two(self):
        template = decode_str(
            """
        Rules:
          Rule1:
            Assertions:
            - Assert: !Equals ["A", "B"]
          Rule2:
            Assertions:
            - Assert: !Equals ["A", "A"]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 0)
        self.assertEqual(len(cfn.conditions._rules), 2)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "e3ae9aa78380b708c78deae1dc0aef69b24d695f",
            ],
        )
        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[1].equals],
            [
                "504e5798cd5ef2173c32fa04cb13291999cead05",
            ],
        )

        self.assertFalse(
            cfn.conditions.satisfiable(
                {},
                {},
            )
        )

    def test_fn_equals_assertions_one(self):
        template = decode_str(
            """
        Rules:
          Rule1:
            Assertions:
            - Assert: !Equals ["A", "A"]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 0)
        self.assertEqual(len(cfn.conditions._rules), 1)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "504e5798cd5ef2173c32fa04cb13291999cead05",
            ],
        )

        self.assertTrue(
            cfn.conditions.satisfiable(
                {},
                {},
            )
        )

    def test_fn_equals_assertions_ref_no_data(self):
        template = decode_str(
            """
        Parameters:
            AccountId:
                Type: String
        Rules:
          Rule1:
            Assertions:
            - Assert: !Equals [!Ref AccountId, !Ref AWS::AccountId]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 0)
        self.assertEqual(len(cfn.conditions._rules), 1)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "9189b0bd9d179a54767b86e0ff6675e6e1c1640d",
            ],
        )

        self.assertTrue(
            cfn.conditions.satisfiable(
                {},
                {},
            )
        )

    def test_fn_equals_assertions_ref_never_satisfiable(self):
        template = decode_str(
            """
        Parameters:
            AccountId:
                Type: String
        Rules:
          Rule1:
            Assertions:
            - Assert: !Equals [!Ref AccountId, !Ref AWS::AccountId]
            - Assert: !Not [!Equals [!Ref AccountId, !Ref AWS::AccountId]]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 0)
        self.assertEqual(len(cfn.conditions._rules), 1)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "9189b0bd9d179a54767b86e0ff6675e6e1c1640d",
                "9189b0bd9d179a54767b86e0ff6675e6e1c1640d",
            ],
        )

        self.assertFalse(
            cfn.conditions.satisfiable(
                {},
                {},
            )
        )

    def test_conditions_with_rules_and_parameters(self):
        template = decode_str(
            """
        Conditions:
            DeployGateway: !Equals
                - !Ref 'DeployGateway'
                - 'true'
            DeployVpc: !Equals
                - !Ref 'DeployVpc'
                - 'true'
        Parameters:
            DeployAnything:
                AllowedValues:
                - 'false'
                - 'true'
                Type: 'String'
            DeployGateway:
                AllowedValues:
                - 'false'
                - 'true'
                Type: 'String'
            DeployVpc:
                AllowedValues:
                - 'false'
                - 'true'
                Type: 'String'
        Rules:
            DeployGateway:
                Assertions:
                - Assert: !Or
                    - !Equals
                        - !Ref 'DeployAnything'
                        - 'true'
                    - !Equals
                        - !Ref 'DeployGateway'
                        - 'false'
            DeployVpc:
                Assertions:
                - Assert: !Or
                    - !Equals
                        - !Ref 'DeployGateway'
                        - 'true'
                    - !Equals
                        - !Ref 'DeployVpc'
                        - 'false'
        Resources:
            InternetGateway:
                Condition: 'DeployGateway'
                Type: 'AWS::EC2::InternetGateway'
            InternetGatewayAttachment:
                Condition: 'DeployVpc'
                Type: 'AWS::EC2::VPCGatewayAttachment'
                Properties:
                    InternetGatewayId: !Ref 'InternetGateway'
                    VpcId: !Ref 'Vpc'
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._conditions), 2)
        self.assertEqual(len(cfn.conditions._rules), 2)

        self.assertListEqual(
            [equal.hash for equal in cfn.conditions._rules[0].equals],
            [
                "1816223f5e09cdd1207303ef4c6c0f4bbe1d7ba3",
                "a629a1fcd96f6545d896132262f1847e1d22ad00",
            ],
        )

        self.assertTrue(
            cfn.conditions.satisfiable(
                {},
                {},
            )
        )

        self.assertTrue(
            cfn.conditions.check_implies({"DeployVpc": True}, "DeployGateway")
        )

        self.assertFalse(
            cfn.conditions.check_implies({"DeployVpc": False}, "DeployGateway")
        )

        self.assertFalse(
            cfn.conditions.check_implies({"DeployGateway": False}, "DeployVpc")
        )


class TestRulesConstrainParameterValues(TestCase):
    """Rule assertions on a parameter vs a literal constrain resolved values"""

    def test_unconditional_not_equals(self):
        template = decode_str(
            """
        Parameters:
          DestinationArn:
            Type: String
            Default: ""
        Rules:
          DestinationRequired:
            Assertions:
            - Assert: !Not [!Equals [!Ref DestinationArn, ""]]
        """
        )[0]

        cfn = Template("", template)
        self.assertFalse(cfn.conditions.satisfiable({}, {"DestinationArn": ""}))
        self.assertTrue(
            cfn.conditions.satisfiable({}, {"DestinationArn": "arn:aws:logs"})
        )
        # no resolved value for the parameter leaves the rule unpinned
        self.assertTrue(cfn.conditions.satisfiable({}, {}))

    def test_rule_condition(self):
        template = decode_str(
            """
        Parameters:
          Environment:
            Type: String
            Default: dev
            AllowedValues: [dev, prod]
          DestinationArn:
            Type: String
            Default: ""
        Rules:
          DestinationRequiredInProd:
            RuleCondition: !Equals [!Ref Environment, prod]
            Assertions:
            - Assert: !Not [!Equals [!Ref DestinationArn, ""]]
        Conditions:
          IsProd: !Equals [!Ref Environment, prod]
        """
        )[0]

        cfn = Template("", template)
        self.assertFalse(
            cfn.conditions.satisfiable({"IsProd": True}, {"DestinationArn": ""})
        )
        self.assertTrue(
            cfn.conditions.satisfiable({"IsProd": False}, {"DestinationArn": ""})
        )
        self.assertTrue(
            cfn.conditions.satisfiable({"IsProd": True}, {"DestinationArn": "arn"})
        )
        self.assertTrue(cfn.conditions.satisfiable({}, {"DestinationArn": ""}))
        self.assertFalse(
            cfn.conditions.satisfiable(
                {}, {"DestinationArn": "", "Environment": "prod"}
            )
        )

    def test_equals_pins_value(self):
        template = decode_str(
            """
        Parameters:
          Engine:
            Type: String
        Rules:
          EngineIsPostgres:
            Assertions:
            - Assert: !Equals [!Ref Engine, postgres]
        """
        )[0]

        cfn = Template("", template)
        self.assertTrue(cfn.conditions.satisfiable({}, {"Engine": "postgres"}))
        self.assertFalse(cfn.conditions.satisfiable({}, {"Engine": "mysql"}))

    def test_or_of_equals(self):
        template = decode_str(
            """
        Parameters:
          Engine:
            Type: String
        Rules:
          EngineIsSupported:
            Assertions:
            - Assert: !Or
              - !Equals [!Ref Engine, postgres]
              - !Equals [!Ref Engine, mysql]
        """
        )[0]

        cfn = Template("", template)
        self.assertTrue(cfn.conditions.satisfiable({}, {"Engine": "postgres"}))
        self.assertTrue(cfn.conditions.satisfiable({}, {"Engine": "mysql"}))
        self.assertFalse(cfn.conditions.satisfiable({}, {"Engine": "oracle"}))

    def test_contains(self):
        template = decode_str(
            """
        Parameters:
          Engine:
            Type: String
        Rules:
          EngineIsSupported:
            Assertions:
            - Assert: !Contains [[postgres, mysql], !Ref Engine]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._rules), 1)
        self.assertTrue(cfn.conditions.satisfiable({}, {"Engine": "postgres"}))
        self.assertTrue(cfn.conditions.satisfiable({}, {"Engine": "mysql"}))
        self.assertFalse(cfn.conditions.satisfiable({}, {"Engine": "oracle"}))

    def test_duplicate_and_static_equals(self):
        template = decode_str(
            """
        Parameters:
          Engine:
            Type: String
        Rules:
          EngineIsPostgres:
            Assertions:
            - Assert: !Equals [!Ref Engine, postgres]
          EngineIsPostgresAgain:
            Assertions:
            - Assert: !Equals [postgres, !Ref Engine]
          AlwaysTrue:
            Assertions:
            - Assert: !Equals [a, a]
        """
        )[0]

        cfn = Template("", template)
        # the same Fn::Equals in two rules is collected once and a static
        # Fn::Equals is not collected
        self.assertEqual(len(cfn.conditions._rule_parameter_equals), 1)
        self.assertTrue(cfn.conditions.satisfiable({}, {"Engine": "postgres"}))
        self.assertFalse(cfn.conditions.satisfiable({}, {"Engine": "mysql"}))

    def test_not_pinned(self):
        template = decode_str(
            """
        Parameters:
          Subnets:
            Type: CommaDelimitedList
          AccountId:
            Type: String
        Rules:
          InUsEast1:
            Assertions:
            - Assert: !Equals [!Ref AWS::Region, us-east-1]
          SameAccount:
            Assertions:
            - Assert: !Equals [!Ref AccountId, !Ref AWS::AccountId]
          NotEmpty:
            Assertions:
            - Assert: !Not [!Equals [!Ref Subnets, ""]]
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._rules), 3)
        # pseudo parameters, Ref against Ref and list values are left alone
        self.assertTrue(
            cfn.conditions.satisfiable(
                {},
                {
                    "AWS::Region": "us-west-2",
                    "AccountId": "123456789012",
                    "Subnets": [""],
                },
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

    def test_assertion_contains_unsupported(self):
        for value in [
            "foo",
            [["a"]],
            [[], {"Ref": "P"}],
            [[{"Ref": "Q"}], {"Ref": "P"}],
            [["a"], "a"],
            [["a"], {"Fn::GetAtt": ["R", "Arn"]}],
        ]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    _Assertion({"Fn::Contains": value}, {})

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
            - Assert: !Equals [!Ref "AWS::Region", "us-east-1"]
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
                - !Not [!Equals [!Ref "AWS::Region", "us-east-1"]]
                - !Equals [!Ref "AWS::Region", "us-east-1"]
          Rule3: []
        """
        )[0]

        cfn = Template("", template)
        self.assertEqual(len(cfn.conditions._rules), 1)
