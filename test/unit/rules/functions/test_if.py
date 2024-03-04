"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Condition, Parameter
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.If import If


@pytest.fixture(scope="module")
def rule():
    rule = If()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={},
        parameters={
            "MyParameter": Parameter(
                {
                    "Type": "String",
                    "Default": "foobar",
                }
            )
        },
        conditions={
            "IsUsEast1": Condition(
                {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}
            )
        },
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::If",
            {"Fn::If": ["IsUsEast1", "foo", "bar"]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::If with to many arguments",
            {"Fn::If": ["IsUsEast1", "foo", "bar", "key"]},
            {"type": "string"},
            [
                ValidationError(
                    "['IsUsEast1', 'foo', 'bar', 'key'] is too long (3)",
                    path=deque(["Fn::If"]),
                    schema_path=deque(["maxItems"]),
                    validator="fn_if",
                ),
            ],
        ),
        (
            "Invalid Fn::If with bad first element",
            {"Fn::If": ["IsUsEast1", {"foo": "bar"}, "bar"]},
            {"type": "string"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string'",
                    path=deque(["Fn::If", 1]),
                    schema_path=deque(["type"]),
                    validator="type",
                ),
            ],
        ),
        (
            "Invalid Fn::If with bad second element",
            {"Fn::If": ["IsUsEast1", "foo", {"foo": "bar"}]},
            {"type": "string"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string'",
                    path=deque(["Fn::If", 2]),
                    schema_path=deque(["type"]),
                    validator="type",
                ),
            ],
        ),
        (
            "Invalid Fn::If a condition that doesn't exist",
            {"Fn::If": ["foo", True, False]},
            {"type": "boolean"},
            [
                ValidationError(
                    "'foo' is not one of ['IsUsEast1']",
                    path=deque(["Fn::If", 0]),
                    schema_path=deque(["enum"]),
                    validator="fn_if",
                    rule=If(),
                ),
            ],
        ),
        (
            "Invalid Fn::If with a resolved value",
            {"Fn::If": ["IsUsEast1", "foo", {"Ref": "MyParameter"}]},
            {"enum": ["foo", "bar"]},
            [
                ValidationError(
                    "{'Ref': 'MyParameter'} is not one of ['foo', 'bar']",
                    path=deque(["Fn::If", 2]),
                    schema_path=deque(["enum"]),
                    validator="enum",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_if(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
