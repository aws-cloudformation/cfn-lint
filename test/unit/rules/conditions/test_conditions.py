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
                    schema_path=deque(
                        ["patternProperties", "^[a-zA-Z0-9&]{1,255}$", "type"]
                    ),
                    validator="type",
                    validator_value="boolean",
                    instance="bad",
                ),
            ],
        )
