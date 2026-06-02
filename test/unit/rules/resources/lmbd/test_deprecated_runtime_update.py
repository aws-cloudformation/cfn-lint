"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from datetime import datetime
from unittest.mock import patch

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
            datetime(2027, 3, 3),
            [
                ValidationError(
                    "Runtime 'python3.7' was deprecated on "
                    "'2023-12-04'. Creation was disabled on "
                    "'2024-01-09' and update on '2027-03-03'. "
                    "Please consider updating to 'python3.14'",
                )
            ],
        ),
        (
            # will be caught by the update rule
            "nodejs",
            datetime(2016, 10, 31),
            [
                ValidationError(
                    "Runtime 'nodejs' was deprecated on "
                    "'2016-08-30'. Creation was disabled on "
                    "'2016-09-30' and update on '2016-10-31'. "
                    "Please consider updating to 'nodejs24.x'",
                )
            ],
        ),
    ],
)
def test_lambda_runtime(instance, date, expected, rule, validator):
    with patch(
        "cfnlint.rules.resources.lmbd.DeprecatedRuntimeUpdate.datetime"
    ) as mock_dt:
        mock_dt.today.return_value = date
        mock_dt.strptime = datetime.strptime
        errs = list(rule.validate(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
