"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from collections import deque

import pytest

from cfnlint.api import lint
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
                    schema_path=deque(["additionalProperties", "type"]),
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
                    schema_path=deque(["additionalProperties", "required"]),
                    path=deque(["Rule1"]),
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Rule names with characters other than letters and digits",
            {
                "Env_Check": {"Assertions": [{"Assert": {"Fn::Equals": ["a", "a"]}}]},
                "Env-Check": {"Assertions": [{"Assert": {"Fn::Equals": ["a", "a"]}}]},
                "Env.Check": {"Assertions": [{"Assert": {"Fn::Equals": ["a", "a"]}}]},
            },
            [],
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


_NESTED_IDS = ("E1020", "E1700", "E1701", "E8003", "W8003")


@pytest.mark.parametrize(
    "name,rules,expected",
    [
        (
            "Rule name CloudFormation accepts",
            {
                "Env_Check": {
                    "Assertions": [{"Assert": {"Fn::Equals": [{"Ref": "Env"}, "a"]}}]
                }
            },
            [],
        ),
        (
            "Fn::Equals with too many arguments",
            {
                "Rule1": {
                    "Assertions": [
                        {"Assert": {"Fn::Equals": [{"Ref": "Env"}, "a", "b"]}}
                    ]
                }
            },
            ["E8003"],
        ),
        (
            "Ref to a parameter that doesn't exist in an assertion",
            {
                "Rule1": {
                    "Assertions": [
                        {"Assert": {"Fn::Equals": [{"Ref": "Missing"}, "a"]}}
                    ]
                }
            },
            ["E1020"],
        ),
        (
            "Ref to a parameter that doesn't exist in a rule condition",
            {
                "Rule1": {
                    "RuleCondition": {"Fn::Equals": [{"Ref": "Missing"}, "a"]},
                    "Assertions": [{"Assert": {"Fn::Equals": [{"Ref": "Env"}, "a"]}}],
                }
            },
            ["E1020"],
        ),
        (
            "Fn::GetAtt is not supported in an assertion",
            {"Rule1": {"Assertions": [{"Assert": {"Fn::GetAtt": ["Topic", "Arn"]}}]}},
            ["E1701"],
        ),
        (
            "Rule condition that always returns the same result",
            {
                "Rule1": {
                    "RuleCondition": {"Fn::Equals": ["a", "a"]},
                    "Assertions": [{"Assert": {"Fn::Equals": [{"Ref": "Env"}, "b"]}}],
                }
            },
            ["W8003"],
        ),
    ],
)
def test_nested_functions(name, rules, expected):
    # a full lint, so the function filter inside Rules is exercised
    template = {
        "Parameters": {"Env": {"Type": "String"}},
        "Rules": rules,
        "Resources": {"Topic": {"Type": "AWS::SNS::Topic"}},
    }

    matches = lint(json.dumps(template), regions=["us-east-1"])
    ids = sorted(match.rule.id for match in matches if match.rule.id in _NESTED_IDS)

    assert ids == expected, f"Test {name!r} got {matches!r}"
