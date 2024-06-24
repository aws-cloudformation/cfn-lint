"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

from cfnlint.context import Context
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.resources.iam.IdentityPolicy import IdentityPolicy


class TestIdentityPolicies(TestCase):
    """Test IAM identity Policies"""

    def setUp(self):
        """Setup"""
        self.rule = IdentityPolicy()

    def test_object_basic(self):
        """Test Positive"""
        validator = CfnTemplateValidator()

        policy = {"Version": "2012-10-18"}

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(errs[0].message, "'Statement' is a required property")
        self.assertListEqual(list(errs[0].path), [])
        self.assertEqual(len(errs), 2, errs)
        self.assertEqual(
            errs[1].message, "'2012-10-18' is not one of ['2008-10-17', '2012-10-17']"
        )
        self.assertListEqual(list(errs[1].path), ["Version"])

    def test_object_multiple_effect(self):
        validator = CfnTemplateValidator()

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "NotAction": "*",
                    "Action": [
                        "cloudformation:*",
                    ],
                    "Resource": "*",
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 2, errs)
        self.assertEqual(
            errs[0].message,
            ("Only one of ['Action', 'NotAction'] is a required property"),
        )
        self.assertEqual(
            errs[1].message,
            ("Only one of ['Action', 'NotAction'] is a required property"),
        )
        self.assertIn(
            ["Statement", 0, "NotAction"], [list(errs[0].path), list(errs[1].path)]
        )
        self.assertIn(
            ["Statement", 0, "Action"], [list(errs[0].path), list(errs[1].path)]
        )

    def test_object_statements(self):
        validator = CfnTemplateValidator({}).evolve(
            context=Context(functions=FUNCTIONS)
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "NotAllow",
                    "Action": [
                        "cloudformation:Describe*",
                        "cloudformation:List*",
                        "cloudformation:Get*",
                    ],
                    "Resource": [
                        {
                            "Fn::Sub": "arn:${AWS::Partition}:iam::123456789012:role/object-role"
                        },
                        {
                            "Fn::Sub": "arn:aws:cloudformation:${AWS::Region}:aws:transform/Serverless-2016-10-31"
                        },
                        {
                            "NotValid": [
                                "arn:${AWS::Partition}:iam::123456789012:role/object-role"
                            ]
                        },
                        "arn:aws:medialive:*",
                    ],
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 2, errs)
        self.assertEqual(errs[0].message, "'NotAllow' is not one of ['Allow', 'Deny']")
        self.assertListEqual(list(errs[0].path), ["Statement", 0, "Effect"])
        self.assertEqual(
            errs[1].message,
            "{'NotValid': ['arn:${AWS::Partition}:iam::123456789012:role/object-role']} is not of type 'string'",
        )
        self.assertListEqual(list(errs[1].path), ["Statement", 0, "Resource", 2])

    def test_string_statements(self):
        """Test Positive"""
        validator = CfnTemplateValidator()

        # ruff: noqa: E501
        policy = """
            {
                "Version": "2012-10-18",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "cloudformation:Describe*",
                            "cloudformation:List*",
                            "cloudformation:Get*"
                        ],
                        "Resource": [
                            "*",
                            {"Fn::Sub": ["arn:${AWS::Partition}:iam::123456789012/role/string-role"]}
                        ]
                    }
                ]
            }
        """

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 2, errs)
        self.assertEqual(
            errs[0].message,
            "{'Fn::Sub': ['arn:${AWS::Partition}:iam::123456789012/role/string-role']} is not of type 'string'",
        )
        self.assertListEqual(list(errs[0].path), ["Statement", 0, "Resource", 1])
        self.assertEqual(
            errs[1].message, "'2012-10-18' is not one of ['2008-10-17', '2012-10-17']"
        )
        self.assertListEqual(list(errs[1].path), ["Version"])
