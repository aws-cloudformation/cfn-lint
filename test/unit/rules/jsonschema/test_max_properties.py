"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.jsonschema.MaxProperties import MaxProperties


class ChildMaxProperties(CloudFormationLintRule):
    id = "ChildMaxProperties"

    def foo(self, validator, awsType, instance, schema):
        if instance == "bar":
            return
        yield ValidationError("Not bar")


class TestMaxProperties(BaseRuleTestCase):
    """Test AWS Types"""

    def setUp(self):
        """Setup"""
        super(TestMaxProperties, self).setUp()
        self.rule = MaxProperties("ChildMaxProperties")
        self.rule.child_rules = {"ChildMaxProperties": ChildMaxProperties()}

    def test_max_properties(self):
        validator = CfnTemplateValidator({})
        self.assertEqual(
            len(list(self.rule.maxProperties(validator, 5, {"foo": True}, {}))),
            0,
        )

        errs = list(
            self.rule.maxProperties(validator, 1, {"foo": True, "bar": True}, {})
        )
        self.assertEqual(len(errs), 1)
        self.assertIsNone(errs[0].rule)

        errs = list(self.rule.maxProperties(validator, 1, {"foo": True}, {}))
        self.assertEqual(len(errs), 1)
        self.assertEqual(errs[0].rule.id, "ChildMaxProperties")
