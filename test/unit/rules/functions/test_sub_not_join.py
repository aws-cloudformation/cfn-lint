"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Resource
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.SubNotJoin import SubNotJoin


@pytest.fixture(scope="module")
def rule():
    rule = SubNotJoin()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={
            "MyResource": Resource({"Type": "AWS::S3::Bucket"}),
        },
        parameters={},
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::Join with proper delimiter",
            {"Fn::Join": [",", ["", ""]]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Join with an empty string",
            {"Fn::Join": ["", ["foo", "bar"]]},
            {"type": "string"},
            [
                ValidationError(
                    "Prefer using Fn::Sub over Fn::Join with an empty delimiter",
                    path=deque(["Fn::Join", 0]),
                    rule=SubNotJoin(),
                )
            ],
        ),
        (
            "Valid Fn::Join with a Fn::Sub",
            {"Fn::Join": ["", ["foo", {"Fn::Sub": ["MyResource", {}]}]]},
            {"type": "string"},
            [],
        ),
        (
            "Invalid Fn::Join with a Ref",
            {"Fn::Join": ["", ["foo", {"Ref": "MyResource"}]]},
            {"type": "string"},
            [
                ValidationError(
                    "Prefer using Fn::Sub over Fn::Join with an empty delimiter",
                    path=deque(["Fn::Join", 0]),
                    rule=SubNotJoin(),
                )
            ],
        ),
        (
            "Invalid Fn::Join with a Fn::Sub",
            {"Fn::Join": ["", ["foo", {"Fn::Sub": "${MyResource}"}]]},
            {"type": "string"},
            [
                ValidationError(
                    "Prefer using Fn::Sub over Fn::Join with an empty delimiter",
                    path=deque(["Fn::Join", 0]),
                    rule=SubNotJoin(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.validate(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
