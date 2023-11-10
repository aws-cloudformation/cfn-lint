"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.jsonschema.MaxLength import MaxLength


class ChildMaxLength(CloudFormationLintRule):
    id = "ChildMaxLength"

    def foo(self, validator, awsType, instance, schema):
        if instance == "bar":
            return
        yield ValidationError("Not bar")


class TestMaxLength(BaseRuleTestCase):
    """Test AWS Types"""

    def setUp(self):
        """Setup"""
        super(TestMaxLength, self).setUp()
        self.rule = MaxLength("ChildMaxLength")
        self.rule.child_rules = {"ChildMaxLength": ChildMaxLength()}

    def test_max_properties(self):
        validator = CfnTemplateValidator({})
        self.assertEqual(
            len(list(self.rule.maxLength(validator, 5, "foo", {}))),
            0,
        )

        errs = list(self.rule.maxLength(validator, 1, "foo", {}))
        self.assertEqual(len(errs), 1)
        self.assertIsNone(errs[0].rule)

        errs = list(self.rule.maxLength(validator, 11, "1234567890", {}))
        self.assertEqual(len(errs), 1)
        self.assertEqual(errs[0].rule.id, "ChildMaxLength")
