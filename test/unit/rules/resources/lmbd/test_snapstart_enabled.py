"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.SnapStartEnabled import SnapStartEnabled


@pytest.fixture(scope="module")
def rule():
    rule = SnapStartEnabled()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "python doesn't need SnapStart",
            "python3.11",
            [],
        ),
        (
            "wrong type",
            [],
            [],
        ),
        (
            "java 8 doesn't need SnapStart",
            "java8",
            [],
        ),
        (
            "java 17 should have SnapStart",
            "java17",
            [
                ValidationError(
                    "'java17' runtime should consider using 'SnapStart'",
                    path=deque(["SnapStart", "ApplyOn"]),
                    rule=SnapStartEnabled(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule):
    errs = list(rule.validate(instance))

    assert errs == expected, f"{name!r}: expected {expected!r} got {errs!r}"
