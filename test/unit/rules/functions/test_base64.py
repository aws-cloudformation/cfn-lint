"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.Base64 import Base64


@pytest.fixture(scope="module")
def rule():
    rule = Base64()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::Base64 string",
            {"Fn::Base64": "foo"},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Base64 for wrong output type",
            {"Fn::Base64": "foo"},
            {"type": "array"},
            [
                ValidationError(
                    "{'Fn::Base64': 'foo'} is not of type 'array'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_base64",
                ),
            ],
        ),
        (
            "Invalid Fn::Base64 is NOT a string",
            {"Fn::Base64": ["foo", "bar"]},
            {"type": "string"},
            [
                ValidationError(
                    "['foo', 'bar'] is not of type 'string'",
                    path=deque(["Fn::Base64"]),
                    schema_path=deque(["type"]),
                    validator="fn_base64",
                ),
            ],
        ),
        (
            "Invalid Fn::Base64 using an invalid function",
            {"Fn::Base64": {"foo": "bar"}},
            {"type": "string"},
            [
                ValidationError(
                    "{'foo': 'bar'} is not of type 'string'",
                    path=deque(["Fn::Base64"]),
                    schema_path=deque(["type"]),
                    validator="fn_base64",
                ),
            ],
        ),
        (
            "Valid Fn::Base64 with a valid function",
            {"Fn::Base64": {"Fn::Sub": "foo"}},
            {"type": "string"},
            [],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_base64(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
