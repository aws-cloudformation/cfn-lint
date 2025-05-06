"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules.functions._BaseFn import BaseFn


class _ChildRule(CloudFormationLintRule):
    id = "XXXXX"


@pytest.fixture(scope="module")
def rule(request):
    rule = BaseFn(resolved_rule="XXXXX")
    rule._schema = request.param.get("schema")

    rule.child_rules["XXXXX"] = _ChildRule()
    yield rule


@pytest.mark.parametrize(
    "name,rule,instance,expected",
    [
        (
            "Dynamic references are ignored",
            {
                "schema": {
                    "enum": ["Foo"],
                },
                "patches": [],
            },
            {"Fn::Sub": "{{resolve:ssm:${AWS::AccountId}/${AWS::Region}/ac}}"},
            [],
        ),
        (
            "Everything is fine",
            {
                "schema": {"enum": ["Foo"]},
                "patches": [],
            },
            {"Fn::Sub": "Foo"},
            [],
        ),
        (
            "Resolved Fn::Sub has no strict type validation",
            {
                "schema": {"type": ["integer"]},
                "patches": [],
            },
            {"Fn::Sub": "2"},
            [],
        ),
        (
            "Standard error",
            {
                "schema": {"enum": ["Foo"]},
                "patches": [],
            },
            {"Fn::Sub": "Bar"},
            [
                ValidationError(
                    message=(
                        "{'Fn::Sub': 'Bar'} is not one of "
                        "['Foo'] when '' is resolved"
                    ),
                    path=deque(["Fn::Sub"]),
                    validator="",
                    schema_path=deque(["enum"]),
                    rule=_ChildRule(),
                )
            ],
        ),
        (
            "Errors with context error",
            {
                "schema": {"anyOf": [{"enum": ["Foo"]}]},
                "patches": [],
            },
            {"Fn::Sub": "Bar"},
            [
                ValidationError(
                    message=(
                        "{'Fn::Sub': 'Bar'} is not valid "
                        "under any of the given schemas "
                        "when '' is resolved"
                    ),
                    path=deque(["Fn::Sub"]),
                    validator="",
                    schema_path=deque(["anyOf"]),
                    rule=_ChildRule(),
                    context=[
                        ValidationError(
                            message=(
                                "{'Fn::Sub': 'Bar'} is not one of "
                                "['Foo'] when '' is resolved"
                            ),
                            path=deque([]),
                            validator="enum",
                            schema_path=deque([0, "enum"]),
                            rule=_ChildRule(),
                        )
                    ],
                )
            ],
        ),
    ],
    indirect=["rule"],
)
def test_resolve(name, instance, expected, validator, rule):
    errs = list(rule.resolve(validator, rule.schema(validator, instance), instance, {}))
    assert errs == expected, f"{name!r} failed and got errors {errs!r}"
