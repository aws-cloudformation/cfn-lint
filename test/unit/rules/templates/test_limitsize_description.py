"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest.mock import ANY, MagicMock

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.templates.LimitDescription import LimitDescription


@pytest.fixture(scope="module")
def rule():
    rule = LimitDescription()
    yield rule


@pytest.mark.parametrize(
    "name,instance,add_rule,child_return_values,expected",
    [
        (
            "Valid description",
            "Foo",
            True,
            [],
            [],
        ),
        (
            "Invalid type",
            {},
            True,
            None,
            [],
        ),
        (
            "Too long",
            "FooBar",
            True,
            None,
            [
                ValidationError(
                    ("expected maximum length: 3, found: 6"),
                )
            ],
        ),
        (
            "Child rule good",
            "Foo",
            True,
            [],
            [],
        ),
        (
            "Child rule bad",
            "Foo",
            True,
            [ValidationError("Bad")],
            [
                ValidationError(
                    ("Bad"),
                )
            ],
        ),
        (
            "Child rule None",
            "Foo",
            False,
            None,
            [],
        ),
    ],
)
def test_validate(
    name, instance, add_rule, child_return_values, expected, rule, validator
):
    child_rule = MagicMock()
    if child_return_values is not None:
        child_rule.maxLength.return_value = iter(child_return_values)

    if add_rule:
        rule.child_rules["I1003"] = child_rule

    errors = list(rule.maxLength(validator, 3, instance, {}))

    assert errors == expected, f"Test {name!r} got {errors!r}"

    if child_return_values is not None:
        assert child_rule.maxLength.mock_calls == [ANY]
    else:
        assert child_rule.maxLength.mock_calls == []
