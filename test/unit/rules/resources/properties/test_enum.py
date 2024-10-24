"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.parameters.Enum import Enum as ParameterEnum
from cfnlint.rules.resources.properties.Enum import Enum


@pytest.fixture
def rule():
    rule = Enum()
    rule.child_rules["W2030"] = ParameterEnum()
    yield Enum()


@pytest.fixture
def template():
    return {
        "Parameters": {
            "MyString": {
                "Type": "String",
                "Default": "a",
                "AllowedValues": ["a", "b"],
            },
        },
        "Resources": {},
    }


@pytest.mark.parametrize(
    "name,instance,enums,path,expected",
    [
        (
            "Validate the standard enum",
            "a",
            ["a"],
            {},
            [],
        ),
        (
            "Validate the standard enum",
            "a",
            ["a"],
            {"value_path": ["Parameters", "MyString", "AllowedValues", 0]},
            [],
        ),
        (
            "Invalid with the standard enum",
            "a",
            ["b"],
            {},
            [
                ValidationError(
                    ("'a' is not one of ['b']"),
                    path=deque([]),
                    schema_path=deque([]),
                    path_override=deque([]),
                ),
            ],
        ),
        (
            "Invalid with the standard enum from parameter",
            "a",
            ["b"],
            {"value_path": ["Parameters", "MyString", "AllowedValues", 0]},
            [
                ValidationError(
                    ("'a' is not one of ['b']"),
                    path=deque([]),
                    schema_path=deque([]),
                    rule=ParameterEnum(),
                    path_override=deque(["Parameters", "MyString", "AllowedValues", 0]),
                ),
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate_enum(name, instance, enums, expected, rule, validator):
    errs = list(rule.enum(validator, enums, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"


@pytest.mark.parametrize(
    "name,instance,enums,path,expected",
    [
        (
            "Validate the standard enum",
            "a",
            ["A"],
            {},
            [],
        ),
        (
            "Validate the standard enum",
            "a",
            ["A"],
            {"value_path": ["Parameters", "MyString", "AllowedValues", 0]},
            [],
        ),
        (
            "Invalid with the standard enum",
            "a",
            ["B"],
            {},
            [
                ValidationError(
                    ("'a' is not one of ['b'] (case-insensitive)"),
                    path=deque([]),
                    schema_path=deque([]),
                    path_override=deque([]),
                ),
            ],
        ),
        (
            "Invalid with the standard enum from parameter",
            "a",
            ["B"],
            {"value_path": ["Parameters", "MyString", "AllowedValues", 0]},
            [
                ValidationError(
                    ("'a' is not one of ['b'] (case-insensitive)"),
                    path=deque([]),
                    schema_path=deque([]),
                    rule=ParameterEnum(),
                    path_override=deque(["Parameters", "MyString", "AllowedValues", 0]),
                ),
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate_enum_case_insensitive(
    name, instance, enums, expected, rule, validator
):
    errs = list(rule.enumCaseInsensitive(validator, enums, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
