"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from unittest import TestCase

from cfnlint.context import Context, Path
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.resources.iam.TrustPolicy import TrustPolicy


class TestTrustPolicy(TestCase):
    """Test IAM trust Policies"""

    def setUp(self):
        """Setup"""
        self.rule = TrustPolicy()

    def test_valid_trust_policy(self):
        """Test a valid trust policy passes"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "AWS": "arn:aws:iam::123456789012:root",
                    },
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertListEqual(errs, [])

    def test_valid_trust_policy_account_id(self):
        """Test a valid trust policy with account ID principal"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "AWS": "123456789012",
                    },
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertListEqual(errs, [])

    def test_valid_trust_policy_wildcard(self):
        """Test a valid trust policy with wildcard principal"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": "*",
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertListEqual(errs, [])

    def test_valid_trust_policy_service(self):
        """Test a valid trust policy with service principal"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "Service": "ec2.amazonaws.com",
                    },
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertListEqual(errs, [])

    def test_malformed_principal_arn_double_colon(self):
        """Test that a malformed ARN with double colon is caught"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "AWS": "arn:aws::iam::123456789012:root",
                    },
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertTrue(len(errs) > 0, "Expected errors for malformed ARN")
        err_messages = [e.message for e in errs]
        self.assertTrue(
            any(
                "is not valid under any of the given schemas" in m for m in err_messages
            ),
            f"Expected anyOf validation error, got: {err_messages}",
        )

    def test_missing_principal(self):
        """Test that missing principal is caught"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertTrue(len(errs) > 0, "Expected errors for missing principal")
        err_messages = [e.message for e in errs]
        self.assertTrue(
            any("Principal" in m for m in err_messages),
            f"Expected Principal required error, got: {err_messages}",
        )

    def test_no_resource_required(self):
        """Test that Resource is NOT required in trust policies"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "AWS": "arn:aws:iam::123456789012:root",
                    },
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        err_messages = [e.message for e in errs]
        self.assertFalse(
            any("Resource" in m for m in err_messages),
            f"Trust policies should not require Resource, got: {err_messages}",
        )

    def test_assumed_role_principal(self):
        """Test a valid assumed role principal"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "AWS": "arn:aws:sts::123456789012:assumed-role/rolename/session",  # noqa: E501
                    },
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertListEqual(errs, [])
