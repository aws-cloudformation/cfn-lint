"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from unittest import TestCase

from jsonschema import Draft7Validator

from cfnlint.rules.resources.iam.IdentityPolicy import (  # pylint: disable=E0401
    IdentityPolicy,
)


class TestIdentityPolicies(TestCase):
    """Test IAM identity Policies"""

    def setUp(self):
        """Setup"""
        self.rule = IdentityPolicy()

    def test_object_basic(self):
        """Test Positive"""
        validator = Draft7Validator(schema={})

        policy = {"Version": "2012-10-18"}

        errs = list(
            self.rule.iamidentitypolicy(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 2, errs)
        self.assertEqual(
            errs[0].message, "'2012-10-18' is not one of ['2008-10-17', '2012-10-17']"
        )
        self.assertListEqual(list(errs[0].path), ["Version"])
        self.assertEqual(errs[1].message, "'Statement' is a required property")
        self.assertListEqual(list(errs[1].path), [])

    def test_object_multiple_effect(self):
        """Test Positive"""
        validator = Draft7Validator(schema={})

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
            self.rule.iamidentitypolicy(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 1, errs)
        self.assertEqual(
            errs[0].message,
            "{'Effect': 'Allow', 'NotAction': '*', 'Action': ['cloudformation:*'], 'Resource': '*'} is valid under each of {'required': ['NotAction']}, {'required': ['Action']}",
        )
        self.assertListEqual(list(errs[0].path), ["Statement", 0])

    def test_object_statements(self):
        """Test Positive"""
        validator = Draft7Validator(schema={})

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
                            "Fn::Sub": [
                                "arn:${AWS::Partition}:iam::123456789012/role/cep-publish-role"
                            ]
                        },
                        {
                            "NotValid": [
                                "arn:${AWS::Partition}:iam::123456789012/role/cep-publish-role"
                            ]
                        },
                    ],
                }
            ],
        }

        errs = list(
            self.rule.iamidentitypolicy(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 2, errs)
        self.assertEqual(errs[0].message, "'NotAllow' is not one of ['Allow', 'Deny']")
        self.assertListEqual(list(errs[0].path), ["Statement", 0, "Effect"])
        self.assertEqual(
            errs[1].message,
            "{'NotValid': ['arn:${AWS::Partition}:iam::123456789012/role/cep-publish-role']} is not of type 'string'",
        )
        self.assertListEqual(list(errs[1].path), ["Statement", 0, "Resource", 1])

    def test_string_statements(self):
        """Test Positive"""
        validator = Draft7Validator(schema={})

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
                            {"Fn::Sub": ["arn:${AWS::Partition}:iam::123456789012/role/cep-publish-role"]}
                        ]
                    }
                ]
            }
        """

        errs = list(
            self.rule.iamidentitypolicy(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 2, errs)
        self.assertEqual(
            errs[0].message,
            "{'Fn::Sub': ['arn:${AWS::Partition}:iam::123456789012/role/cep-publish-role']} is not of type 'string'",
        )
        self.assertListEqual(list(errs[0].path), ["Statement", 0, "Resource", 1])
        self.assertEqual(
            errs[1].message, "'2012-10-18' is not one of ['2008-10-17', '2012-10-17']"
        )
        self.assertListEqual(list(errs[1].path), ["Version"])
