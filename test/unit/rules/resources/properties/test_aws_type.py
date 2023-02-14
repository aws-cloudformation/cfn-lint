"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.resources.properties.AwsType import AwsType  # pylint: disable=E0401


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
        self.rule.types = {"foo": "AnId"}

    def test_aws_type(self):
        validator = Draft7Validator({})
        self.assertEqual(len(list(self.rule.awsType(validator, "foo", "bar", {}))), 0)
        self.assertEqual(len(list(self.rule.awsType(validator, "foo", "foo", {}))), 1)
