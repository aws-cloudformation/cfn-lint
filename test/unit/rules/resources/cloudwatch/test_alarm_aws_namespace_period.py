"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.cloudwatch.AlarmAwsNamespacePeriod import (
    AlarmAwsNamespacePeriod,
)


@pytest.fixture(scope="module")
def rule():
    rule = AlarmAwsNamespacePeriod()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Namespace": "AWS/foo",
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
                "Namespace": "AWS/foo",
                "Period": {"Ref": "Period"},  # ignore when object
            },
            [],
        ),
        (
            {
                "Namespace": {"Ref": "Namespace"},  # ignore when object
                "Period": 30,
            },
            [],
        ),
        (
            {
                "Namespace": "AWS/foo",
                "Period": 30,
            },
            [
                ValidationError(
                    "30 is less than the minimum of 60",
                    rule=AlarmAwsNamespacePeriod(),
                    path=deque(["Period"]),
                    validator="minimum",
                    schema={"minimum": 60, "type": ["number", "string"]},
                    schema_path=deque(["then", "properties", "Period", "minimum"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
