"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ecs.ServiceHealthCheckGracePeriodSeconds import (
    ServiceHealthCheckGracePeriodSeconds,
)


@pytest.fixture(scope="module")
def rule():
    rule = ServiceHealthCheckGracePeriodSeconds()
    yield rule


@pytest.fixture
def template():
    return {
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}
        },
    }


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"HealthCheckGracePeriodSeconds": "Foo", "LoadBalancers": ["Bar"]},
            [],
        ),
        (
            {"LoadBalancers": []},
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {"HealthCheckGracePeriodSeconds": "Foo", "LoadBalancers": []},
            [
                ValidationError(
                    "expected minimum item count: 1, found: 0",
                    rule=ServiceHealthCheckGracePeriodSeconds(),
                    path=deque(["LoadBalancers"]),
                    validator="minItems",
                    schema_path=deque(
                        ["then", "then", "properties", "LoadBalancers", "minItems"]
                    ),
                )
            ],
        ),
        (
            {
                "HealthCheckGracePeriodSeconds": "Foo",
            },
            [
                ValidationError(
                    "'LoadBalancers' is a required property",
                    rule=ServiceHealthCheckGracePeriodSeconds(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                )
            ],
        ),
        (
            {
                "HealthCheckGracePeriodSeconds": "Foo",
                "LoadBalancers": [
                    {"Fn::If": ["IsUsEast1", "Bar", {"Ref": "AWS::NoValue"}]}
                ],
            },
            [
                ValidationError(
                    "expected minimum item count: 1, found: 0",
                    rule=ServiceHealthCheckGracePeriodSeconds(),
                    path=deque(["LoadBalancers"]),
                    validator="minItems",
                    schema_path=deque(
                        ["then", "then", "properties", "LoadBalancers", "minItems"]
                    ),
                )
            ],
        ),
        (
            {
                "HealthCheckGracePeriodSeconds": "Foo",
                "LoadBalancers": {
                    "Fn::If": ["IsUsEast1", ["Bar"], {"Ref": "AWS::NoValue"}]
                },
            },
            [
                ValidationError(
                    "'LoadBalancers' is a required property",
                    rule=ServiceHealthCheckGracePeriodSeconds(),
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
