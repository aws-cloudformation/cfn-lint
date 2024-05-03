"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.properties.ImageId import ImageId


@pytest.fixture(scope="module")
def rule():
    rule = ImageId()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        path=deque([]),
        resources={},
        parameters={
            "MyImageId": Parameter(
                {
                    "Type": "AWS::EC2::Image::Id",
                }
            ),
            "MyString": Parameter(
                {
                    "Type": "String",
                }
            ),
        },
    )
    yield CfnTemplateValidator(context=context)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid Ref to a paraemter",
            {"Ref": "MyImageId"},
            [],
        ),
        (
            "Valid Ref to a Pseudo-Parameter",
            {"Ref": "AWS::Region"},
            [],
        ),
        (
            "Invalid Ref to a parameter of the wrong type",
            {"Ref": "MyString"},
            [
                ValidationError(
                    (
                        "'String' is not one of ['AWS::EC2::Image::Id'"
                        ", 'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>']"
                    ),
                    path=deque([]),
                    schema_path=deque(["enum"]),
                    validator="enum",
                    rule=ImageId(),
                    path_override=deque(["Parameters", "MyString", "Type"]),
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
