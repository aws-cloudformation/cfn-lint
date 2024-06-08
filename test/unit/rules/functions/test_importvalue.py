"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.ImportValue import ImportValue


@pytest.fixture(scope="module")
def rule():
    rule = ImportValue()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::ImportValue with a string",
            {"Fn::ImportValue": "foo"},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::ImportValue with an invalid type",
            {"Fn::ImportValue": ["foo"]},
            {"type": "string"},
            [
                ValidationError(
                    "['foo'] is not of type 'string'",
                    path=deque(["Fn::ImportValue"]),
                    schema_path=deque(["type"]),
                    validator="fn_importvalue",
                )
            ],
        ),
        (
            "Invalid Fn::ImportValue with an invalid output type",
            {"Fn::ImportValue": "foo"},
            {"type": "array"},
            [
                ValidationError(
                    "{'Fn::ImportValue': 'foo'} is not of type 'array'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_importvalue",
                ),
            ],
        ),
        (
            "Valid Fn::ImportValue with a function",
            {"Fn::ImportValue": {"Fn::Sub": "foo"}},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::ImportValue with an invalid function",
            {"Fn::ImportValue": {"Fn::Split": "foo"}},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::Split': 'foo'} is not of type 'string'",
                    path=deque(["Fn::ImportValue"]),
                    schema_path=deque(["type"]),
                    validator="fn_importvalue",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_importvalue(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
