"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.properties.ImageId import ImageId


@pytest.fixture(scope="module")
def rule():
    rule = ImageId()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {
            "MyImageId": {
                "Type": "AWS::EC2::Image::Id",
            },
            "MyString": {
                "Type": "String",
            },
        },
        "Resources": {},
    }


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid Ref to a paraemter",
            "MyImageId",
            [],
        ),
        (
            "Valid Ref to a Pseudo-Parameter",
            "AWS::Region",
            [],
        ),
        (
            "Invalid Ref to a parameter of the wrong type",
            "MyString",
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
