"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

from cfnlint.context import Context
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.resources.iam.ResourcePolicy import ResourcePolicy


class TestResourcePolicy(TestCase):
    """Test IAM identity Policies"""

    def setUp(self):
        """Setup"""
        self.rule = ResourcePolicy()

    def test_object_basic(self):
        """Test Positive"""
        validator = CfnTemplateValidator()

        policy = {"Version": "2012-10-18"}

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 2, errs)
        self.assertEqual(errs[0].message, "'Statement' is a required property")
        self.assertListEqual(list(errs[0].path), [])
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
                    "Principal": {
                        "AWS": [
                            "arn:aws:iam::123456789012:root",
                            "999999999999",
                            "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity E1234ABCDE12AB",
                        ],
                        "CanonicalUser": "79a59df900b949e55d96a1e698fbacedfd6e09d98eacf8f8d5218e7cd47ef2be",
                    },
                    "Condition": {
                        "Null": {
                            "s3:x-amz-server-side-encryption": [False],
                            "aws:TagKeys": False,
                        }
                    },
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
                            "NotValid": [
                                "arn:${AWS::Partition}:iam::123456789012:role/object-role"
                            ]
                        },
                    ],
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 3, errs)
        self.assertEqual(
            errs[0].message,
            "Only one of ['Principal', 'NotPrincipal'] is a required property",
        )
        self.assertEqual(errs[1].message, "'NotAllow' is not one of ['Allow', 'Deny']")
        self.assertListEqual(list(errs[1].path), ["Statement", 0, "Effect"])
        self.assertEqual(
            errs[2].message,
            "{'NotValid': ['arn:${AWS::Partition}:iam::123456789012:role/object-role']} is not of type 'string'",
        )
        self.assertListEqual(list(errs[2].path), ["Statement", 0, "Resource", 1])

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
        self.assertEqual(len(errs), 3, errs)
        self.assertEqual(
            errs[0].message,
            "Only one of ['Principal', 'NotPrincipal'] is a required property",
        )
        self.assertEqual(
            errs[1].message,
            "{'Fn::Sub': ['arn:${AWS::Partition}:iam::123456789012/role/string-role']} is not of type 'string'",
        )
        self.assertListEqual(list(errs[1].path), ["Statement", 0, "Resource", 1])
        self.assertEqual(
            errs[2].message, "'2012-10-18' is not one of ['2008-10-17', '2012-10-17']"
        )
        self.assertListEqual(list(errs[2].path), ["Version"])

    def test_principal_wildcard(self):
        validator = CfnTemplateValidator({}).evolve(
            context=Context(functions=FUNCTIONS)
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": {
                        "Fn::Sub": "arn:${AWS::Partition}:iam::123456789012:role/object-role"
                    },
                    "Principal": "*",
                },
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": {
                        "Fn::Sub": "arn:${AWS::Partition}:iam::123456789012:role/object-role"
                    },
                    "Principal": {
                        "AWS": "*",
                    },
                },
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": {
                        "Fn::Sub": "arn:${AWS::Partition}:iam::123456789012:role/object-role"
                    },
                    "Principal": {"Fn::Sub": "*"},
                },
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertListEqual(errs, [])

    def test_assumed_role(self):
        validator = CfnTemplateValidator({}).evolve(
            context=Context(functions=FUNCTIONS)
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "arn:aws:s3:::bucket",
                    "Principal": {
                        "AWS": "arn:aws:sts::123456789012:assumed-role/rolename/rolesessionname"
                    },
                },
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertListEqual(errs, [])
