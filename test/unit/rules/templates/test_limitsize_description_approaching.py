"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.templates.ApproachingLimitDescription import (
    ApproachingLimitDescription,
)


@pytest.fixture(scope="module")
def rule():
    rule = ApproachingLimitDescription()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid description",
            "a" * 18,
            [],
        ),
        (
            "Too long",
            "a" * 19,
            [
                ValidationError(
                    f"'{'a'*19}' is approaching the max length of 20",
                    rule=ApproachingLimitDescription(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errors = list(rule.maxLength(validator, 20, instance, {}))

    assert errors == expected, f"Test {name!r} got {errors!r}"
