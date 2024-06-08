"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.metadata.InterfaceConfiguration import InterfaceConfiguration


@pytest.fixture(scope="module")
def rule():
    rule = InterfaceConfiguration()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {
            "Foo": {"Type": "String"},
            "Bar": {"Type": "String"},
        },
    }


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid Interface",
            {
                "ParameterGroups": [
                    {
                        "Label": "A Group",
                        "Parameters": [
                            "Foo",
                            "Bar",
                        ],
                    }
                ],
                "ParameterLabels": {"Foo": {"default": "a parameter"}},
            },
            [],
        ),
        (
            "Extra properties",
            {"Foo": "Bar"},
            [
                ValidationError(
                    ("Additional properties are not allowed " "('Foo' was unexpected)"),
                    validator="additionalProperties",
                    schema_path=deque(["additionalProperties"]),
                    rule=InterfaceConfiguration(),
                    path=deque(["Foo"]),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
