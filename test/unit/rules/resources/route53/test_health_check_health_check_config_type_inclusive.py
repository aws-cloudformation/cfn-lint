"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.route53.HealthCheckHealthCheckConfigTypeInclusive import (
    HealthCheckHealthCheckConfigTypeInclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = HealthCheckHealthCheckConfigTypeInclusive()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Type": "CLOUDWATCH_METRIC", "AlarmIdentifier": "Foo"},
            [],
        ),
        (
            {
                "Type": {"Ref": "AWS::Region"},
            },
            [],
        ),
        (
            [],
            [],
        ),
        (
            {
                "Type": "CLOUDWATCH_METRIC",
            },
            [
                ValidationError(
                    "'AlarmIdentifier' is a required property",
                    rule=HealthCheckHealthCheckConfigTypeInclusive(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
