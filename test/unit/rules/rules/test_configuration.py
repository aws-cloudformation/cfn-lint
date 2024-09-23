"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.rules.Configuration import Configuration


@pytest.fixture(scope="module")
def rule():
    rule = Configuration()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Empty is okay",
            {},
            [],
        ),
        (
            "wrong type",
            [],
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(["type"]),
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Wrong type of rule",
            {
                "Rule1": [],
            },
            [
                ValidationError(
                    "[] is not of type 'object'",
                    validator="type",
                    schema_path=deque(["patternProperties", "^[A-Za-z0-9]+$", "type"]),
                    path=deque(["Rule1"]),
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Empty rule",
            {
                "Rule1": {},
            },
            [
                ValidationError(
                    "'Assertions' is a required property",
                    validator="required",
                    schema_path=deque(
                        ["patternProperties", "^[A-Za-z0-9]+$", "required"]
                    ),
                    path=deque(["Rule1"]),
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Valid rule with RuleCondition and Assertions",
            {
                "Rule1": {
                    "RuleCondition": {"Fn::Equals": ["a", "b"]},
                    "Assertions": [
                        {
                            "Assert": {"Fn::Equals": ["a", "b"]},
                            "AssertDescription": "a is equal to b",
                        },
                        {
                            "Assert": {"Fn::Equals": ["a", "b"]},
                        },
                    ],
                },
            },
            [],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
