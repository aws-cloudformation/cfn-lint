"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.ToJsonString import ToJsonString


@pytest.fixture(scope="module")
def rule():
    rule = ToJsonString()
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
            "Fn::ToJsonString is invalid with wrong output type",
            {"Fn::ToJsonString": {"foo": "bar"}},
            {"type": "object"},
            [
                ValidationError(
                    "{'Fn::ToJsonString': {'foo': 'bar'}} is not of type 'object'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_tojsonstring",
                ),
            ],
        ),
        (
            "Fn::ToJsonString is valid array with functions",
            {"Fn::ToJsonString": [{"Ref": "MyResource"}]},
            {"type": "string"},
            [],
        ),
        (
            "Fn::ToJsonString is valid object with functions",
            {"Fn::ToJsonString": {"Key": {"Ref": "MyResource"}}},
            {"type": "string"},
            [],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_tojsonstring(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
