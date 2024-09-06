"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ecs.FargateDeploymentSchedulingStrategy import (
    FargateDeploymentSchedulingStrategy,
)


@pytest.fixture(scope="module")
def rule():
    rule = FargateDeploymentSchedulingStrategy()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "LaunchType": "FARGATE",
            },
            [],
        ),
        (
            {
                "LaunchType": "FARGATE",
                "SchedulingStrategy": "REPLICA",
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "LaunchType": "FARGATE",
                "SchedulingStrategy": {"Ref": "Replica"},
            },
            [],
        ),
        (
            {
                "LaunchType": "EXTERNAL",
                "SchedulingStrategy": "DAEMON",
            },
            [],
        ),
        (
            {
                "LaunchType": "EXTERNAL",
                "SchedulingStrategy": "DAEMON",
                "DeploymentController": {"Type": "ECS"},
            },
            [],
        ),
        (
            {
                "LaunchType": "EXTERNAL",
                "SchedulingStrategy": "DAEMON",
                "DeploymentController": {"Type": "CODE_DEPLOY"},
            },
            [
                ValidationError(
                    "'REPLICA' was expected",
                    rule=FargateDeploymentSchedulingStrategy(),
                    path=deque(["SchedulingStrategy"]),
                    validator="const",
                    schema_path=deque(
                        ["then", "properties", "SchedulingStrategy", "const"]
                    ),
                )
            ],
        ),
        (
            {
                "LaunchType": "FARGATE",
                "SchedulingStrategy": "DAEMON",
            },
            [
                ValidationError(
                    "'REPLICA' was expected",
                    rule=FargateDeploymentSchedulingStrategy(),
                    path=deque(["SchedulingStrategy"]),
                    validator="const",
                    schema_path=deque(
                        ["then", "properties", "SchedulingStrategy", "const"]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
