"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.cloudwatch.AlarmPeriod import AlarmPeriod


@pytest.fixture(scope="module")
def rule():
    rule = AlarmPeriod()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Period": 60,
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "Period": {"Ref": "Period"},  # ignore when object
            },
            [],
        ),
        (
            {
                "Period": 30,
            },
            [],
        ),
        (
            {
                "Period": 600,
            },
            [],
        ),
        (
            {
                "Period": 45,
            },
            [
                ValidationError(
                    "45 is not one of [10, 30, 60] or a multiple of 60",
                    rule=AlarmPeriod(),
                    path=deque(["Period"]),
                    validator="enum",
                    schema_path=deque(["then", "properties", "Period", "then", "enum"]),
                )
            ],
        ),
        (
            {
                "Period": "45",
            },
            [
                ValidationError(
                    "'45' is not one of [10, 30, 60] or a multiple of 60",
                    rule=AlarmPeriod(),
                    path=deque(["Period"]),
                    validator="enum",
                    schema_path=deque(["then", "properties", "Period", "then", "enum"]),
                )
            ],
        ),
        (
            {
                "Period": 121,
            },
            [
                ValidationError(
                    "121 is not one of [10, 30, 60] or a multiple of 60",
                    rule=AlarmPeriod(),
                    path=deque(["Period"]),
                    validator="multipleOf",
                    schema_path=deque(
                        ["then", "properties", "Period", "else", "multipleOf"]
                    ),
                )
            ],
        ),
        (
            {
                "Period": "121",
            },
            [
                ValidationError(
                    "'121' is not one of [10, 30, 60] or a multiple of 60",
                    rule=AlarmPeriod(),
                    path=deque(["Period"]),
                    validator="multipleOf",
                    schema_path=deque(
                        ["then", "properties", "Period", "else", "multipleOf"]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
