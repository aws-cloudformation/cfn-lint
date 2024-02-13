"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
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
        parameters={},
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::If",
            {"Fn::If": ["condition", "foo", "bar"]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::If with to many arguments",
            {"Fn::If": ["condition", "foo", "bar", "key"]},
            {"type": "string"},
            [
                ValidationError(
                    "['condition', 'foo', 'bar', 'key'] is too long (3)",
                    path=deque(["Fn::If"]),
                    schema_path=deque(["maxItems"]),
                    validator="fn_if",
                ),
            ],
        ),
        (
            "Invalid Fn::If with bad first element",
            {"Fn::If": ["condition", {"foo": "bar"}, "bar"]},
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
            "Invalid Fn::If with bad first element",
            {"Fn::If": ["condition", "foo", {"foo": "bar"}]},
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
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_if(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
