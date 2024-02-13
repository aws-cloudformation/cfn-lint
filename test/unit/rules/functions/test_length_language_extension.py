"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.Length import Length


@pytest.fixture(scope="module")
def rule():
    rule = Length()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={},
        parameters={},
        transforms=Transforms(["AWS::LanguageExtensions"]),
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Fn::Length valid structure",
            {"Fn::Length": []},
            {"type": "integer"},
            [],
        ),
        (
            "Fn::Length invalid type",
            {"Fn::Length": "foo"},
            {"type": "integer"},
            [
                ValidationError(
                    "'foo' is not of type 'array'",
                    path=deque(["Fn::Length"]),
                    schema_path=deque(["type"]),
                    validator="fn_length",
                ),
            ],
        ),
        (
            "Fn::Length invalid output type",
            {"Fn::Length": ["foo"]},
            {"type": "array"},
            [
                ValidationError(
                    "{'Fn::Length': ['foo']} is not of type 'array'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_length",
                ),
            ],
        ),
        (
            "Fn::Length using valid function",
            {"Fn::Length": {"Fn::GetAZs": ""}},
            {"type": "integer"},
            [],
        ),
        (
            "Fn::Length using valid functions in array",
            {"Fn::Length": [{"Ref": "MyResource"}]},
            {"type": "integer"},
            [],
        ),
        (
            "Fn::Length is not supported",
            {"Fn::Length": []},
            {"type": "integer"},
            [],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_length(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
