"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.SubUnneeded import SubUnneeded


@pytest.fixture(scope="module")
def rule():
    rule = SubUnneeded()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        ("Valid with matching parameters", ["${Foo}", {"Foo": "Bar"}], []),
        (
            "Invalid with a variables",
            ["Foo", {"Foo": "Bar", "Bar": "Foo"}],
            [
                ValidationError(
                    "'Fn::Sub' isn't needed because there are no variables", path=[0]
                ),
            ],
        ),
        (
            "Invalid with a string",
            "Foo",
            [
                ValidationError(
                    "'Fn::Sub' isn't needed because there are no variables", path=[]
                )
            ],
        ),
    ],
)
def test_sub_unneeded(name, instance, expected, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))
    assert errors == expected, f"Test {name!r} got {errors!r}"
