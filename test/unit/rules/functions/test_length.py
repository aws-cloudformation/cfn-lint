"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.context.context import Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.Length import Length
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = Length()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {},
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,schema,context_evolve,expected",
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
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
        ),
        (
            "Fn::Length invalid type",
            {"Fn::Length": "foo"},
            {"type": "integer"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [
                ValidationError(
                    "'foo' is not of type 'array'",
                    path=deque(["Fn::Length"]),
                    schema_path=deque(["type"]),
                    validator="fn_length",
                    rule=Length(),
                ),
            ],
        ),
        (
            "Fn::Length invalid output type",
            {"Fn::Length": ["foo"]},
            {"type": "array"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
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
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
        ),
        (
            "Fn::Length using valid functions in array",
            {"Fn::Length": [{"Ref": "MyResource"}]},
            {"type": "integer"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
        ),
        (
            "Fn::Length is not supported",
            {"Fn::Length": []},
            {"type": "integer"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
        ),
        (
            "Fn::Length output while a number can be a string",
            {"Fn::Length": []},
            {"type": "string"},
            {"transforms": Transforms(["AWS::LanguageExtensions"])},
            [],
        ),
    ],
)
def test_validate(name, instance, schema, context_evolve, expected, rule, context, cfn):
    context = context.evolve(**context_evolve)
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.fn_length(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
