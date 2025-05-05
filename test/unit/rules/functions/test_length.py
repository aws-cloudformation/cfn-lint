"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.Length import Length


@pytest.fixture
def rule():
    rule = Length()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,template,expected",
    [
        (
            "Fn::Length is not supported",
            {"Fn::Length": []},
            {"type": "integer"},
            {},
            [
                ValidationError(
                    (
                        "Fn::Length is not supported without "
                        "'AWS::LanguageExtensions' transform"
                    ),
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_length",
                    rule=Length(),
                ),
            ],
        ),
        (
            "Fn::Length valid structure",
            {"Fn::Length": []},
            {"type": "integer"},
            {"Transform": ["AWS::LanguageExtensions"]},
            [],
        ),
        (
            "Fn::Length invalid type",
            {"Fn::Length": "foo"},
            {"type": "integer"},
            {"Transform": ["AWS::LanguageExtensions"]},
            [
                ValidationError(
                    "'foo' is not of type 'array'",
                    path=deque(["Fn::Length"]),
                    schema_path=deque(["cfnContext", "schema", "type"]),
                    validator="fn_length",
                    rule=Length(),
                ),
            ],
        ),
        (
            "Fn::Length invalid output type",
            {"Fn::Length": ["foo"]},
            {"type": "array"},
            {"Transform": ["AWS::LanguageExtensions"]},
            [
                ValidationError(
                    "{'Fn::Length': ['foo']} is not of type 'array'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_length",
                    rule=Length(),
                ),
            ],
        ),
        (
            "Fn::Length using valid function",
            {"Fn::Length": {"Fn::GetAZs": ""}},
            {"type": "integer"},
            {"Transform": ["AWS::LanguageExtensions"]},
            [],
        ),
        (
            "Fn::Length using valid functions in array",
            {"Fn::Length": [{"Ref": "MyResource"}]},
            {"type": "integer"},
            {"Transform": ["AWS::LanguageExtensions"]},
            [],
        ),
        (
            "Fn::Length is not supported",
            {"Fn::Length": []},
            {"type": "integer"},
            {"Transform": ["AWS::LanguageExtensions"]},
            [],
        ),
        (
            "Fn::Length output while a number can be a string",
            {"Fn::Length": []},
            {"type": "string"},
            {"Transform": ["AWS::LanguageExtensions"]},
            [],
        ),
    ],
    indirect=["template"],
)
def test_validate(name, instance, schema, expected, validator, rule):
    errs = list(rule.fn_length(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
