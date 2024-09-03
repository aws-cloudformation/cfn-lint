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
def rule():
    rule = BaseFn(resolved_rule="XXXXX")
    rule.child_rules["XXXXX"] = _ChildRule()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Dynamic references are ignored",
            {"Fn::Sub": "{{resolve:ssm:${AWS::AccountId}/${AWS::Region}/ac}}"},
            {"enum": ["Foo"]},
            [],
        ),
        ("Everything is fine", {"Fn::Sub": "Foo"}, {"enum": ["Foo"]}, []),
        (
            "Resolved Fn::Sub has no strict type validation",
            {"Fn::Sub": "2"},
            {"type": ["integer"]},
            [],
        ),
        (
            "Standard error",
            {"Fn::Sub": "Bar"},
            {"enum": ["Foo"]},
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
            {"Fn::Sub": "Bar"},
            {"anyOf": [{"enum": ["Foo"]}]},
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
)
def test_resolve(name, instance, schema, expected, validator, rule):
    errs = list(rule.resolve(validator, schema, instance, {}))
    assert errs == expected, f"{name!r} failed and got errors {errs!r}"
