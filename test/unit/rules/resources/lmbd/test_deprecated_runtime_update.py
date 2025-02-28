"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from datetime import datetime

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.DeprecatedRuntimeUpdate import DeprecatedRuntimeUpdate


@pytest.fixture(scope="module")
def rule():
    rule = DeprecatedRuntimeUpdate()
    yield rule


@pytest.mark.parametrize(
    "instance,date,expected",
    [
        (
            "nodejs16.x",
            datetime(2023, 12, 14),
            [],
        ),
        (
            "foo",  # not existent runtime
            datetime(2023, 12, 14),
            [],
        ),
        (
            {},  # wrong type
            datetime(2023, 12, 14),
            [],
        ),
        (
            "python3.7",
            datetime(2025, 11, 2),
            [
                ValidationError(
                    (
                        "Runtime 'python3.7' was deprecated on "
                        "'2023-12-04'. Creation was disabled on "
                        "'2024-01-09' and update on '2025-11-01'. "
                        "Please consider updating to 'python3.13'"
                    ),
                )
            ],
        ),
        (
            # will be caught by the update rule
            "nodejs",
            datetime(2016, 10, 31),
            [
                ValidationError(
                    (
                        "Runtime 'nodejs' was deprecated on "
                        "'2016-10-31'. Creation was disabled on "
                        "'2016-10-31' and update on '2016-10-31'. "
                        "Please consider updating to 'nodejs22.x'"
                    ),
                )
            ],
        ),
    ],
)
def test_lambda_runtime(instance, date, expected, rule, validator):
    rule.current_date = date
    errs = list(rule.validate(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
