"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter, Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.jsonschema._validators_cfn import FnItems
from cfnlint.rules.functions.Ref import Ref


@pytest.fixture(scope="module")
def rule():
    rule = Ref()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={},
        parameters={
            "MyParameter": Parameter({"Type": "String"}),
            "MyArrayParameter": Parameter({"Type": "CommaDelimitedList"}),
        },
        transforms=Transforms(["AWS::LanguageExtensions"]),
    )
    yield CfnTemplateValidator({}).extend(
        validators={
            "fn_items": FnItems().validate,
            "ref": Ref().ref,
        }
    )(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid ref",
            {"Ref": {"Ref": "MyParameter"}},
            {"type": "string"},
            [],
        ),
        (
            "Invalid second ref with array return",
            {"Ref": {"Ref": "MyArrayParameter"}},
            {"type": "array"},
            [
                ValidationError(
                    "{'Ref': 'MyArrayParameter'} is not of type 'string'",
                    path=deque(["Ref"]),
                    validator="ref",
                    schema_path=deque(["ref"]),
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.ref(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
