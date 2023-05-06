"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.rules.parameters.AllowedValue import AllowedValue as ParameterAllowedValue
from cfnlint.rules.resources.properties.AllowedValue import (
    AllowedValue,  # pylint: disable=E0401
)
from cfnlint.template import Template


class TestAllowedValue(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""

    def setUp(self):
        """Setup"""
        self.rule = AllowedValue()
        cfn = Template(
            "test.yaml",
            {
                "Parameters": {
                    "Foo": {"Type": "String", "Default": "Bar"},
                }
            },
            regions=["us-east-1"],
        )
        self.rule.child_rules["W2030"] = ParameterAllowedValue()
        self.rule.initialize(cfn)
        self.rule.child_rules["W2030"].initialize(cfn)

    def test_allowed_value(self):
        """Test Positive"""

        validator = Draft7Validator({"type": "string", "enum": ["a", "b"]})
        self.assertEqual(len(list(self.rule.enum(validator, ["a", "b"], "a", {}))), 0)
        self.assertEqual(len(list(self.rule.enum(validator, ["a", "b"], "c", {}))), 1)
        self.assertEqual(len(list(self.rule.enum(validator, [0, 2], 0, {}))), 0)
        self.assertEqual(len(list(self.rule.enum(validator, [0, 2], 1, {}))), 1)

        self.assertEqual(len(list(self.rule.enum(validator, [0], 0, {}))), 0)
        self.assertEqual(len(list(self.rule.enum(validator, [1], 0, {}))), 1)

        self.assertEqual(len(list(self.rule.enum(validator, [True], 0, {}))), 1)
        self.assertEqual(len(list(self.rule.enum(validator, [True], 1, {}))), 1)
        self.assertEqual(len(list(self.rule.enum(validator, [False], 0, {}))), 1)
        self.assertEqual(len(list(self.rule.enum(validator, [False], 1, {}))), 1)

        self.assertEqual(
            len(list(self.rule.enum(validator, [0], {"Ref": "Foo"}, {}))), 1
        )

        ## fall back to enum validation and not doing Ref
        self.assertEqual(
            len(
                list(
                    self.rule.enum(
                        validator,
                        ["Bar"],
                        {"Ref": "Foo", "Fn::GetAtt": "ResourceName"},
                        {},
                    )
                )
            ),
            1,
        )
        self.assertEqual(
            len(
                list(
                    self.rule.enum(
                        validator, ["Bar"], {"Fn::GetAtt": "ResourceName"}, {}
                    )
                )
            ),
            0,
        )

    def test_list_if(self):
        """Test if"""
        rule = AllowedValue()
        validator = Draft7Validator({"type": "string", "enum": ["a", "b"]})
        self.assertEqual(
            len(
                list(
                    rule.validate_if(validator, ["a", "b"], ["Condition", "c", "d"], {})
                )
            ),
            2,
        )
        self.assertEqual(
            len(list(rule.validate_if(validator, 1, ["Condition", 2], {}))),
            0,
        )
