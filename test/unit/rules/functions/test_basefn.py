"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context.parameters import ParameterSet
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


@pytest.fixture
def template():
    return {"Parameters": {"MyString": {"Type": "String"}}}


@pytest.mark.parametrize(
    "name,instance,schema,parameters,expected",
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
            [],
        ),
        ("Everything is fine", {"Fn::Sub": "Foo"}, {"enum": ["Foo"]}, {}, []),
        (
            "Resolved Fn::Sub has no strict type validation",
            {
                "schema": {"type": ["integer"]},
                "patches": [],
            },
            {"Fn::Sub": "2"},
            [],
            [],
        ),
        (
            "Standard error",
            {
                "schema": {"enum": ["Foo"]},
                "patches": [],
            },
            {"Fn::Sub": "Bar"},
            {"enum": ["Foo"]},
            [],
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
            {"anyOf": [{"enum": ["Foo"]}]},
            [],
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
        (
            "Ref of a parameter with parameter set",
            {"Ref": "MyString"},
            {"enum": ["Foo"]},
            [
                ParameterSet(
                    parameters={"MyString": "Bar"},
                    source=None,
                )
            ],
            [
                ValidationError(
                    message=(
                        "{'Ref': 'MyString'} is not one of "
                        "['Foo'] when '' is resolved to 'Bar'"
                    ),
                    path=deque(["Ref"]),
                    validator="",
                    schema_path=deque(["enum"]),
                    rule=_ChildRule(),
                )
            ],
        ),
        (
            "Fn::Sub of a parameter with parameter set",
            {"Fn::Sub": "${MyString}"},
            {"enum": ["Foo"]},
            [
                ParameterSet(
                    parameters={"MyString": "Bar"},
                    source=None,
                )
            ],
            [
                ValidationError(
                    message=(
                        "{'Fn::Sub': '${MyString}'} is not one of "
                        "['Foo'] when '' is resolved"
                    ),
                    path=deque(["Fn::Sub"]),
                    validator="",
                    schema_path=deque(["enum"]),
                    rule=_ChildRule(),
                )
            ],
        ),
    ],
    indirect=["parameters"],
)
def test_resolve(name, instance, schema, parameters, expected, validator, rule):
    errs = list(rule.resolve(validator, schema, instance, {}))
    assert errs == expected, f"{name!r} failed and got errors {errs!r}"
