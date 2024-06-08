"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.events.RuleScheduleExpression import RuleScheduleExpression


@pytest.fixture(scope="module")
def rule():
    rule = RuleScheduleExpression()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "wrong format",
            [],
            [],
        ),
        (
            "10:15 AM (UTC) every day",
            "cron(15 10 * * ? *)",
            [],
        ),
        (
            "6:00 PM Monday through Friday",
            "cron(0 18 ? * MON-FRI *)",
            [],
        ),
        (
            "8:00 AM on the first day of the month",
            "cron(0 8 1 * ? *)",
            [],
        ),
        (
            "Every 10 min on weekdays",
            "cron(0/10 * ? * MON-FRI *)",
            [],
        ),
        (
            "Every 5 minutes between 8:00 AM and 5:55 PM weekdays",
            "cron(0/5 8-17 ? * MON-FRI *)",
            [],
        ),
        (
            "9:00 AM on the first Monday of each month",
            "cron(0 9 ? * 2#1 *)",
            [],
        ),
        (
            "Every 5 minutes",
            "rate(5 minutes)",
            [],
        ),
        (
            "Every hour",
            "rate(1 hour)",
            [],
        ),
        (
            "Every seven days",
            "rate(7 days)",
            [],
        ),
        (
            "has to be cron() or rate()",
            "daily",
            [
                ValidationError(
                    ("'daily' has to be either 'cron()' or 'rate()'"),
                )
            ],
        ),
        (
            "Empty cron",
            "cron()",
            [
                ValidationError(
                    ("'' is not of type 'string'"),
                )
            ],
        ),
        (
            "Empty rate",
            "rate()",
            [
                ValidationError(
                    ("'' is not of type 'string'"),
                )
            ],
        ),
        (
            "Not enough values",
            "rate(5)",
            [
                ValidationError(
                    ("'5' has to be of format rate(Value Unit)"),
                )
            ],
        ),
        (
            "Value has to be a digit",
            "rate(five minutes)",
            [
                ValidationError(
                    ("'five' is not of type 'integer'"),
                )
            ],
        ),
        (
            "Not enough values",
            "cron(0 */1 * * WED)",
            [
                ValidationError(
                    (
                        (
                            "'0' is not of length 6. (Minutes Hours "
                            "Day-of-month Month Day-of-week Year)"
                        )
                    ),
                )
            ],
        ),
        (
            (
                "Specify the Day-of-month and Day-of-week "
                "fields in the same cron expression"
            ),
            "cron(* 1 * * * *)",
            [
                ValidationError(
                    (
                        (
                            "'*' specifies both Day-of-month and "
                            "Day-of-week. (Minutes Hours "
                            "Day-of-month Month Day-of-week Year)"
                        )
                    ),
                )
            ],
        ),
        (
            "Value of 1 should be singular. 'minute' not 'minutes'",
            "rate(1 minutes)",
            [
                ValidationError(
                    ("'minutes' is not one of ['minute', 'hour', 'day']"),
                )
            ],
        ),
        (
            "Value has to be greater than 0",
            "rate(0 hour)",
            [
                ValidationError(
                    ("'0' is less than the minimum of 0"),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):

    errs = list(rule.validate(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
