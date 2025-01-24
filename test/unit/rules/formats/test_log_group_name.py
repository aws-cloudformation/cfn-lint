"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.LogGroupName import LogGroupName


@pytest.fixture(scope="module")
def rule():
    rule = LogGroupName()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid log group name",
            "123457",
            True,
        ),
        (
            "Valid with invalid type",
            [],
            True,
        ),
        (
            "Valid log group name with special characters",
            "aws/one.two-three#four_five",
            True,
        ),
        ("Invalid log group name because of special character", "foo&bar", False),
        ("Invalid log group name because of empty", "", False),
        ("Invalid log group name because too long", "a" * 513, False),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
