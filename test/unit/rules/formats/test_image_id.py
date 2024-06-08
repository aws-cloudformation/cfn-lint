"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.ImageId import ImageId


@pytest.fixture(scope="module")
def rule():
    rule = ImageId()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid image id",
            "ami-abcd1234",
            True,
        ),
        (
            "Valid image id long",
            "ami-abcdefa1234567890",
            True,
        ),
        (
            "Valid type",
            [],
            True,
        ),
        ("Invalid image ID", "ami-abc", False),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
