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

    def test_invalid_trust_policy_wildcard_string(self):
        """Test a trust policy with the string form Principal '*' is rejected.

        IAM CreateRole rejects the bare string form in a trust policy
        ("invalid principal: STAR"); only the object form {"AWS": "*"} is valid.
        """
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
        self.assertTrue(len(errs) > 0, "Expected errors for string Principal '*'")
        err_messages = [e.message for e in errs]
        self.assertTrue(
            any("is not of type 'object'" in m for m in err_messages),
            f"Expected object type error, got: {err_messages}",
        )

    def test_valid_trust_policy_aws_wildcard_object(self):
        """Test a trust policy with the object form {"AWS": "*"} still passes"""
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
                        "AWS": "*",
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

    def test_invalid_trust_policy_not_principal(self):
        """Test that NotPrincipal is rejected in a trust policy.

        IAM does not allow the NotPrincipal element in a role trust policy;
        CreateRole fails with "AssumeRole policy must not contain NotPrincipal field".
        """
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
                    "Effect": "Deny",
                    "Action": "sts:AssumeRole",
                    "NotPrincipal": {
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
        self.assertTrue(len(errs) > 0, "Expected errors for NotPrincipal")
        err_messages = [e.message for e in errs]
        self.assertTrue(
            any("NotPrincipal" in m for m in err_messages),
            f"Expected NotPrincipal error, got: {err_messages}",
        )

    def test_invalid_trust_policy_group_principal(self):
        """Test that an IAM group ARN is rejected as a trust policy principal.

        IAM does not allow identifying a user group as a principal in a policy;
        CreateRole fails with 'Invalid principal in policy'.
        """
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
                        "AWS": "arn:aws:iam::123456789012:group/my-group",
                    },
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertTrue(len(errs) > 0, "Expected errors for group ARN principal")
        err_messages = [e.message for e in errs]
        self.assertTrue(
            any(
                "is not valid under any of the given schemas" in m for m in err_messages
            ),
            f"Expected anyOf validation error, got: {err_messages}",
        )

    def test_valid_trust_policy_user_principal(self):
        """Test a trust policy with a user ARN principal still passes"""
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
                        "AWS": "arn:aws:iam::123456789012:user/alice",
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

    def test_sts_root_and_federated_user_principals(self):
        """Test sts root and federated-user principals, which IAM accepts"""
        validator = CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

        for principal in (
            "arn:aws:sts::123456789012:root",
            "arn:aws-cn:sts::123456789012:federated-user/example",
            "arn:aws-us-gov:sts::123456789012:federated-user/example",
        ):
            with self.subTest(principal=principal):
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "sts:AssumeRole",
                            "Principal": {"AWS": principal},
                        }
                    ],
                }

                errs = list(
                    self.rule.validate(
                        validator=validator,
                        policy=policy,
                        schema={},
                        policy_type=None,
                    )
                )
                self.assertListEqual(errs, [])

    def test_unsupported_sts_principal(self):
        """Test that an unsupported sts principal is caught"""
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
                    "Principal": {"AWS": "arn:aws:sts::123456789012:user/example"},
                }
            ],
        }

        errs = list(
            self.rule.validate(
                validator=validator, policy=policy, schema={}, policy_type=None
            )
        )
        self.assertTrue(errs)

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

    def _validator(self):
        return CfnTemplateValidator({}).evolve(
            context=Context(
                functions=FUNCTIONS,
                path=Path(
                    cfn_path=deque(["Resources", "AWS::IAM::Role", "Properties"])
                ),
            )
        )

    def _errs(self, principal):
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": principal,
                }
            ],
        }
        return list(
            self.rule.validate(
                validator=self._validator(),
                policy=policy,
                schema={},
                policy_type=None,
            )
        )

    def test_trust_principal_other_keys_valid(self):
        """Test string and array forms of the non-AWS principal keys pass"""
        for key in ("CanonicalUser", "Federated", "Service"):
            for value in ("example", ["example", "other"]):
                with self.subTest(key=key, value=value):
                    self.assertListEqual(self._errs({key: value}), [])

    def test_trust_principal_other_keys_invalid_type(self):
        """Test that a non-string, non-array value is caught"""
        for key in ("CanonicalUser", "Federated", "Service"):
            with self.subTest(key=key):
                errs = self._errs({key: 42})
                self.assertEqual(len(errs), 1, errs)
                self.assertEqual(errs[0].message, "42 is not of type 'string', 'array'")

    def test_trust_principal_other_keys_invalid_item_type(self):
        """Test that a non-string array item is caught"""
        for key in ("CanonicalUser", "Federated", "Service"):
            with self.subTest(key=key):
                errs = self._errs({key: [{"a": "b"}]})
                self.assertEqual(len(errs), 1, errs)
                self.assertEqual(errs[0].message, "{'a': 'b'} is not of type 'string'")

    def test_trust_principal_other_keys_with_aws_sibling(self):
        """Test the non-AWS principal keys pass alongside an AWS principal"""
        for key in ("CanonicalUser", "Federated", "Service"):
            with self.subTest(key=key):
                self.assertListEqual(
                    self._errs(
                        {
                            key: "example",
                            "AWS": "arn:aws:iam::123456789012:root",
                        }
                    ),
                    [],
                )

    def test_trust_principal_other_keys_unresolvable(self):
        """Test that unresolvable values on the non-AWS principal keys pass"""
        unresolvable = (
            {"Ref": "MyParameter"},
            {"Fn::GetAtt": ["MyResource", "Arn"]},
            {"Fn::If": ["MyCondition", "example", "other"]},
        )
        for key in ("CanonicalUser", "Federated", "Service"):
            for value in unresolvable:
                with self.subTest(key=key, value=value):
                    self.assertListEqual(self._errs({key: value}), [])

    def test_trust_principal_other_keys_absent(self):
        """Test a principal with none of the non-AWS keys present passes"""
        self.assertListEqual(self._errs({"AWS": "arn:aws:iam::123456789012:root"}), [])
