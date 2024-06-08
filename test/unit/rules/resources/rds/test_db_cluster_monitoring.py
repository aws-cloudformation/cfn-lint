"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbClusterMonitoring import DbClusterMonitoring


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterMonitoring()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid monitoring configuration",
            {
                "MonitoringInterval": 1,
                "MonitoringRoleArn": "arn",
            },
            [],
        ),
        (
            "Valid empty monitoring",
            {},
            [],
        ),
        (
            "Invalid with just monitoringInterval",
            {"MonitoringInterval": "1"},
            [
                ValidationError(
                    (
                        "You must have 'MonitoringRoleArn' specified "
                        "with 'MonitoringInterval' greater than 0"
                    ),
                    rule=DbClusterMonitoring(),
                    path=deque([]),
                    schema_path=deque(["else", "then", "required"]),
                    validator="required",
                )
            ],
        ),
        (
            "Invalid with just monitoringRoleArn",
            {
                "MonitoringRoleArn": "arn",
            },
            [
                ValidationError(
                    (
                        "You must have 'MonitoringRoleArn' specified "
                        "with 'MonitoringInterval' greater than 0"
                    ),
                    rule=DbClusterMonitoring(),
                    path=deque([]),
                    schema_path=deque(["then", "required"]),
                    validator="required",
                )
            ],
        ),
        (
            "Invalid with MonitoringInterval is 0",
            {
                "MonitoringRoleArn": "arn",
                "MonitoringInterval": "0",
            },
            [
                ValidationError(
                    (
                        "You must have 'MonitoringRoleArn' specified "
                        "with 'MonitoringInterval' greater than 0"
                    ),
                    rule=DbClusterMonitoring(),
                    path=deque(["MonitoringInterval"]),
                    schema_path=deque(
                        ["then", "properties", "MonitoringInterval", "exclusiveMinimum"]
                    ),
                    validator="exclusiveMinimum",
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Test {name!r} for expected {expected!r} got {errs!r}"
