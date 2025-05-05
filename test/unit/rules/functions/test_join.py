"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.Join import Join


@pytest.fixture(scope="module")
def rule():
    rule = Join()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::Join with array",
            {"Fn::Join": ["foo", ["bar"]]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Join with wrong output type",
            {"Fn::Join": ["foo", ["bar"]]},
            {"type": "array"},
            [
                ValidationError(
                    "{'Fn::Join': ['foo', ['bar']]} is not of type 'array'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_join",
                ),
            ],
        ),
        (
            "Invalid Fn::Join is NOT a array",
            {"Fn::Join": "foo"},
            {"type": "string"},
            [
                ValidationError(
                    "'foo' is not of type 'array'",
                    path=deque(["Fn::Join"]),
                    schema_path=deque(["cfnContext", "schema", "type"]),
                    validator="fn_join",
                ),
            ],
        ),
        (
            "Invalid Fn::Join using a function for delimiter",
            {"Fn::Join": [{"Ref": "MyResource"}, ["bar"]]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Ref': 'MyResource'} is not of type 'string'",
                    path=deque(["Fn::Join", 0]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            0,
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_join",
                ),
            ],
        ),
        (
            "Invalid Fn::Join using an invalid function",
            {"Fn::Join": ["-", {"foo": "bar"}]},
            {"type": "string"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'array'",
                    path=deque(["Fn::Join", 1]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            1,
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_join",
                ),
            ],
        ),
        (
            "Invalid Fn::Join using an invalid CFN function",
            {"Fn::Join": ["-", {"Fn::Join": ["-", "bar"]}]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::Join': ['-', 'bar']} is not of type 'array'",
                    path=deque(["Fn::Join", 1]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            1,
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_join",
                ),
            ],
        ),
        (
            "Valid Fn::Join with a valid function",
            {"Fn::Join": ["-", {"Fn::Split": ["-", "bar"]}]},
            {"type": "string"},
            [],
        ),
        (
            "Valid Fn::Join with a valid item function",
            {"Fn::Join": ["-", [{"Fn::Sub": "bar"}]]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Join with an invalid function",
            {"Fn::Join": ["-", [{"Fn::Split": ["-", {"Ref": "MyResource"}]}]]},
            {"type": "string"},
            [
                ValidationError(
                    (
                        "{'Fn::Split': ['-', {'Ref': 'MyResource'}]} "
                        "is not of type 'string'"
                    ),
                    path=deque(["Fn::Join", 1, 0]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            1,
                            "cfnContext",
                            "schema",
                            "items",
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_join",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_join(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
