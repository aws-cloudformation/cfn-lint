"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Map
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.Select import Select


@pytest.fixture(scope="module")
def rule():
    rule = Select()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={},
        parameters={},
        mappings={
            "A": Map({"B": {"C": "D"}}),
        },
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::Select with array",
            {"Fn::Select": [1, ["bar"]]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Select is NOT a array",
            {"Fn::Select": "foo"},
            {"type": "string"},
            [
                ValidationError(
                    "'foo' is not of type 'array'",
                    path=deque(["Fn::Select"]),
                    schema_path=deque(["type"]),
                    validator="fn_select",
                ),
            ],
        ),
        (
            "Invalid Fn::Select using an invalid function for index",
            {"Fn::Select": [{"Fn::GetAtt": "MyResource"}, ["bar"]]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::GetAtt': 'MyResource'} is not of type 'integer'",
                    path=deque(["Fn::Select", 0]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_select",
                ),
            ],
        ),
        (
            "Invalid Fn::Select using an invalid function for array",
            {"Fn::Select": [1, {"foo": "bar"}]},
            {"type": "string"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'array'",
                    path=deque(["Fn::Select", 1]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_select",
                ),
            ],
        ),
        (
            "Invalid Fn::Select using an invalid CFN function",
            {"Fn::Select": [1, {"Fn::Join": ["-", "bar"]}]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::Join': ['-', 'bar']} is not of type 'array'",
                    path=deque(["Fn::Select", 1]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_select",
                ),
            ],
        ),
        (
            "Valid Fn::Select with a valid function",
            {"Fn::Select": [1, {"Fn::Split": ["-", "bar"]}]},
            {"type": "string"},
            [],
        ),
        (
            "Valid Fn::Select with a valid function (FindInMap)",
            {"Fn::Select": [1, ["foo", {"Fn::FindInMap": ["A", "B", "C"]}]]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Select with an invalid function",
            {"Fn::Select": [1, ["foo", {"foo": "bar"}]]},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "{'Fn::Select': [1, ['foo', {'foo': 'bar'}]]} is not of type "
                        "'string' when 'Fn::Select' is resolved"
                    ),
                    path=deque(["Fn::Select"]),
                    schema_path=deque(["type"]),
                    validator="fn_select",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_select(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
