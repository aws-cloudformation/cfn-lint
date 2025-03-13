"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest import TestCase

from cfnlint.context import Context
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
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

    def test_string_statements_with_condition(self):
        validator = CfnTemplateValidator()

        policy = """
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": "*",
                        "Resource": "*",
                        "Condition": {
                            "iam:PassedToService": "cloudformation.amazonaws.com",
                            "StringEquals": {"aws:PrincipalTag/job-category": "iamuser-admin"},
                            "StringLike": {"s3:prefix": ["", "home/", "home/${aws:username}/"]},
                            "ArnLike": {"aws:SourceArn": "arn:aws:cloudtrail:*:111122223333:trail/*"},
                            "NumericLessThanEquals": {"s3:max-keys": "10"},
                            "DateGreaterThan": {"aws:TokenIssueTime": "2020-01-01T00:00:01Z"},
                            "Bool": { "aws:SecureTransport": "false"},
                            "BinaryEquals": { "key" : "QmluYXJ5VmFsdWVJbkJhc2U2NA=="},
                            "IpAddress": {"aws:SourceIp": "203.0.113.0/24"},
                            "ArnEquals": {"aws:SourceArn": "arn:aws:sns:REGION:123456789012:TOPIC-ID"},
                            "StringLikeIfExists": { "ec2:InstanceType": [ "t1.*", "t2.*" ]},
                            "Null":{"aws:TokenIssueTime":"true"},
                            "ForAllValues:StringEquals":{"aws:PrincipalTag/job-category":["iamuser-admin","iamuser-read-only"]},
                            "ForAnyValue:StringEquals":{"aws:PrincipalTag/job-category":"iamuser-admin"},
                            "ForAllValues:StringLike": {"aws:TagKeys": ["key1*"]}
                        }
                    }
                ]
            }
        """

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 1, errs)
        self.assertTrue(
            errs[0].message.startswith("'iam:PassedToService' does not match")
        )
        self.assertListEqual(
            list(errs[0].path), ["Statement", 0, "Condition", "iam:PassedToService"]
        )

    def test_duplicate_sid(self):
        validator = CfnTemplateValidator()

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "All",
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*",
                },
                {
                    "Sid": "All",
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*",
                },
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertEqual(len(errs), 1, errs)
        self.assertEqual(errs[0].message, "array items are not unique for keys ['Sid']")
        self.assertListEqual(list(errs[0].path), ["Statement"])

    def test_pattern_sid(self):
        validator = CfnTemplateValidator()

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "A ",
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*",
                },
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertListEqual(
            errs,
            [
                ValidationError(
                    message="'A ' does not match '^[A-Za-z0-9]+$'",
                    validator="pattern",
                    path=deque(["Statement", 0, "Sid"]),
                    schema_path=deque(
                        [
                            "properties",
                            "Statement",
                            "items",
                            "properties",
                            "Sid",
                            "pattern",
                        ]
                    ),
                    rule=IdentityPolicy(),
                )
            ],
        )
