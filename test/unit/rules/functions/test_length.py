"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
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
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Fn::Length is not supported",
            {"Fn::Length": []},
            {"type": "integer"},
            [
                ValidationError(
                    (
                        "Fn::Length is not supported without "
                        "'AWS::LanguageExtensions' transform"
                    ),
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_length",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_length(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
