"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from collections import deque
from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.conditions.Condition import Condition


class TestCondition(BaseRuleTestCase):
    """Test Base Json Schema"""

    def test_condition(self):
        rule = Condition()
        validator = CfnTemplateValidator({})

        errors = list(rule.cfncondition(validator, {}, True, []))
        self.assertListEqual(
            errors,
            [],
        )

        errors = list(rule.cfncondition(validator, {}, {"bar": "bad"}, []))
        self.assertListEqual(
            errors,
            [
                ValidationError(
                    "{'bar': 'bad'} is not of type 'boolean'",
                    path=deque([]),
                    schema_path=deque(["type"]),
                    validator="type",
                    validator_value="boolean",
                    instance={"bar": "bad"},
                ),
            ],
        )
