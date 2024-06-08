"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.templates.Description import Description


@pytest.fixture(scope="module")
def rule():
    rule = Description()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid description",
            "My Description",
            [],
        ),
        (
            "Invalid type",
            {},
            [
                ValidationError(
                    ("{} is not of type 'string'"),
                    rule=Description(),
                    schema_path=deque(["type"]),
                    validator="type",
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errors = list(rule.validate(validator, False, instance, {}))
    # we use error counts in this one as the instance types are
    # always changing so we aren't going to hold ourselves up by that
    assert errors == expected, f"Test {name!r} got {errors!r}"
