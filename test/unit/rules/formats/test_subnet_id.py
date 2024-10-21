"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.SubnetId import SubnetId


@pytest.fixture(scope="module")
def rule():
    rule = SubnetId()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid subnet id",
            "subnet-abcd1234",
            True,
        ),
        (
            "Valid subnet id long",
            "subnet-abcdefa1234567890",
            True,
        ),
        (
            "Valid but wrong type",
            [],
            True,
        ),
        ("Invalid subnet ID", "subnet-abc", False),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
