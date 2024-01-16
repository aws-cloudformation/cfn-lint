"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.jsonschema.AwsType import AwsType  # pylint: disable=E0401


class ValidType(CloudFormationLintRule):
    id = "AnId"

    def foo(self, validator, awsType, instance, schema):
        if instance == "bar":
            return
        yield ValidationError("Not bar")


class TestAwsType(BaseRuleTestCase):
    """Test AWS Types"""

    def setUp(self):
        """Setup"""
        super(TestAwsType, self).setUp()
        self.rule = AwsType()
        self.rule.child_rules = {"AnId": ValidType()}
        self.rule.types = {
            "foo": "AnId",
            "bar": "AnId",
        }

    def test_aws_type(self):
        validator = CfnTemplateValidator
        self.assertListEqual(
            list(self.rule.awsType(validator, "foo", "bar", {})),
            [],
            list(self.rule.awsType(validator, "foo", "bar", {})),
        )
        self.assertListEqual(
            list(self.rule.awsType(validator, "foo", "foo", {})),
            [ValidationError("Not bar")],
        )
        self.assertListEqual(
            list(self.rule.awsType(validator, "foobar", {}, {})),
            [],
        )
        self.assertListEqual(
            list(self.rule.awsType(validator, "bar", {}, {})),
            [],
        )
