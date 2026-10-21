"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.conditions.Configuration import Configuration


class TestConfiguration(BaseRuleTestCase):
    def test_condition(self):
        rule = Configuration()
        validator = CfnTemplateValidator({})

        errors = list(rule.validate(validator, {}, {"foo": True}, []))
        self.assertListEqual(
            errors,
            [],
        )

        errors = list(rule.validate(validator, {}, {"bar": "bad"}, []))
        self.assertListEqual(
            errors,
            [
                ValidationError(
                    "'bad' is not of type 'boolean'",
                    path=deque(["bar"]),
                    rule=Configuration(),
                    schema_path=deque(["additionalProperties", "type"]),
                    validator="type",
                    validator_value="boolean",
                    instance="bad",
                ),
            ],
        )

    def test_condition_names_accepted_by_cloudformation(self):
        # Regression test for https://github.com/aws-cloudformation/cfn-lint/issues/4770
        # CloudFormation places no character set or length limit on condition
        # logical IDs (all of these were deployed successfully), so E8001 must
        # not flag the names.  The value type check still applies.
        rule = Configuration()
        validator = CfnTemplateValidator({})

        names = [
            "us-east-1",
            "HasDDB-SSE",
            "gamma-eu-west-2",
            "Has.Dot",
            "Has:Colon",
            "Has Space",
            "Has/Slash",
            "IsProd?",
            "X" * 256,
        ]
        instance = {name: {"Fn::Equals": ["a", "b"]} for name in names}
        errors = list(rule.validate(validator, {}, instance, []))
        self.assertListEqual(errors, [])

    def test_condition_invalid_values_still_reported(self):
        # The value type check from #4770 stays: a condition with two function
        # keys and a list-valued condition are both rejected by CreateStack.
        rule = Configuration()
        validator = CfnTemplateValidator({})

        errors = list(
            rule.validate(
                validator,
                {},
                {"Bad": {"Fn::Equals": ["a", "b"], "Fn::Not": [{"Condition": "X"}]}},
                [],
            )
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("is not of type 'boolean'", errors[0].message)

        errors = list(rule.validate(validator, {}, {"Bad": ["Fn::Equals"]}, []))
        self.assertEqual(len(errors), 1)
        self.assertIn("is not of type 'boolean'", errors[0].message)
