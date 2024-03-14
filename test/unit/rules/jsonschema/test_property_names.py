"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.jsonschema.PropertyNames import PropertyNames


class ChildPropertyNames(CloudFormationLintRule):
    id = "ChildMaxPropertyNames"


class TestPropertyNames(BaseRuleTestCase):
    """Test AWS Types"""

    def setUp(self):
        """Setup"""
        super(TestPropertyNames, self).setUp()
        self.rule = PropertyNames("ChildMaxPropertyNames")
        self.rule.child_rules = {"ChildMaxPropertyNames": ChildPropertyNames()}

    def test_property_names(self):
        validator = CfnTemplateValidator({})
        self.assertEqual(
            len(
                list(
                    self.rule.propertyNames(
                        validator, {"maxLength": 10}, {"foo": True}, {}
                    )
                )
            ),
            0,
        )

        errs = list(
            self.rule.propertyNames(validator, {"maxLength": 2}, {"foo": True}, {})
        )
        self.assertEqual(len(errs), 1)
        self.assertEqual(errs[0].rule.id, "")

        errs = list(
            self.rule.propertyNames(validator, {"maxLength": 3}, {"foo": True}, {})
        )
        self.assertEqual(len(errs), 1)
        self.assertEqual(errs[0].rule.id, "ChildMaxPropertyNames")

        errs = list(self.rule.propertyNames(validator, {"maxLength": 3}, [], {}))
        self.assertListEqual(errs, [])

    def test_max_length(self):
        validator = CfnTemplateValidator({})
        self.assertListEqual(list(self.rule._max_length(validator, 3, [], {})), [])


class ChildPropertyNamesWithFunction(CloudFormationLintRule):
    id = "ChildMaxPropertyNamesWithFunction"

    def maxLength(self, validator, s, instance, schema):
        yield ValidationError("test", rule=self)
        yield ValidationError("test", rule=self)


class TestPropertyNamesWithFunction(BaseRuleTestCase):
    """Test AWS Types"""

    def setUp(self):
        """Setup"""
        super(TestPropertyNamesWithFunction, self).setUp()
        self.rule = PropertyNames("ChildMaxPropertyNamesWithFunction")
        self.rule.child_rules = {
            "ChildMaxPropertyNamesWithFunction": ChildPropertyNamesWithFunction()
        }

    def test_property_names(self):
        validator = CfnTemplateValidator({})

        errs = list(
            self.rule.propertyNames(validator, {"maxLength": 3}, {"foo": True}, {})
        )
        self.assertEqual(len(errs), 2)
        self.assertEqual(errs[0].rule.id, "ChildMaxPropertyNamesWithFunction")


class TestPropertyNamesNoChild(BaseRuleTestCase):
    """Test AWS Types"""

    def setUp(self):
        """Setup"""
        super(TestPropertyNamesNoChild, self).setUp()
        self.rule = PropertyNames("ChildMaxPropertyNamesWithFunction")
        self.rule.child_rules = {"ChildMaxPropertyNamesWithFunction": None}

    def test_property_names(self):
        validator = CfnTemplateValidator({})

        errs = list(
            self.rule.propertyNames(validator, {"maxLength": 3}, {"foo": True}, {})
        )
        self.assertEqual(len(errs), 0)
