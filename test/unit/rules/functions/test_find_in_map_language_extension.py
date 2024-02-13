"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Map, Transforms
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.FindInMap import FindInMap


@pytest.fixture(scope="module")
def rule():
    rule = FindInMap()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={},
        mappings={
            "A": Map({"B": {"C": "Value"}}),
        },
        transforms=Transforms(["AWS::LanguageExtensions"]),
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::FindInMap",
            {"Fn::FindInMap": ["A", "B", "C", {"DefaultValue": "D"}]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::FindInMap options not of type object",
            {"Fn::FindInMap": ["A", "B", "C", []]},
            {"type": "string"},
            [
                ValidationError(
                    "[] is not of type 'object'",
                    path=deque(["Fn::FindInMap", 3]),
                    schema_path=deque(["fn_items", "type"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
        (
            "Invalid Fn::FindInMap default keyword doesn't exist",
            {"Fn::FindInMap": ["A", "B", "C", {}]},
            {"type": "string"},
            [
                ValidationError(
                    "'DefaultValue' is a required property",
                    path=deque(["Fn::FindInMap", 3]),
                    schema_path=deque(["fn_items", "required"]),
                    validator="fn_findinmap",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_findinmap(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
