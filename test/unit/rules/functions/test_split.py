"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.Split import Split


@pytest.fixture(scope="module")
def rule():
    rule = Split()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyResource": {
                "Type": "AWS::S3::Bucket",
            },
        },
    }


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::Split with array",
            {"Fn::Split": ["foo", "bar"]},
            {"type": "array"},
            [],
        ),
        (
            "Invalid Fn::Split with wrong output type",
            {"Fn::Split": ["foo", "bar"]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::Split': ['foo', 'bar']} is not of type 'string'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_split",
                ),
            ],
        ),
        (
            "Invalid Fn::Split is NOT a array",
            {"Fn::Split": "foo"},
            {"type": "array"},
            [
                ValidationError(
                    "'foo' is not of type 'array'",
                    path=deque(["Fn::Split"]),
                    schema_path=deque(["type"]),
                    validator="fn_split",
                ),
            ],
        ),
        (
            "Invalid Fn::Split using a function for delimiter",
            {"Fn::Split": [{"foo": "bar"}, "bar"]},
            {"type": "array"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string'",
                    path=deque(["Fn::Split", 0]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_split",
                ),
            ],
        ),
        (
            "Invalid Fn::Split using an invalid function",
            {"Fn::Split": ["-", {"foo": "bar"}]},
            {"type": "array"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string'",
                    path=deque(["Fn::Split", 1]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_split",
                ),
            ],
        ),
        (
            "Invalid Fn::Split using an invalid CFN function",
            {"Fn::Split": ["-", {"Fn::Split": ["-", "bar"]}]},
            {"type": "array"},
            [
                ValidationError(
                    "{'Fn::Split': ['-', 'bar']} is not of type 'string'",
                    path=deque(["Fn::Split", 1]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_split",
                )
            ],
        ),
        (
            "Valid Fn::Split with a valid function",
            {"Fn::Split": ["foo", {"Fn::Sub": "bar"}]},
            {"type": "array"},
            [],
        ),
        (
            "Invalid Fn::Split with a dynamic reference",
            {"Fn::Split": ["foo", "{{resolve:ssm:Foo:1}}"]},
            {"type": "array"},
            [
                ValidationError(
                    "'Fn::Split' does not support dynamic references",
                    path=deque(["Fn::Split", 1]),
                    validator="fn_split",
                )
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_split(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
