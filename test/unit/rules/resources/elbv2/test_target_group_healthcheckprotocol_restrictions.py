"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError

# ruff: noqa: E501
from cfnlint.rules.resources.elasticloadbalancingv2.TargetGroupHealthCheckProtocolRestrictions import (
    TargetGroupHealthCheckProtocolRestrictions,
)


@pytest.fixture(scope="module")
def rule():
    rule = TargetGroupHealthCheckProtocolRestrictions()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"HealthCheckProtocol": "HTTPS", "Matcher": {}},
            [],
        ),
        (
            {"HealthCheckProtocol": "TCP"},
            [],
        ),
        (
            [],
            [],
        ),
        (
            {"HealthCheckProtocol": "TCP", "Matcher": {}},
            [],
        ),
        (
            {"HealthCheckProtocol": "TCP", "Matcher": {"HttpCode": "200-299"}},
            [
                ValidationError(
                    "Additional properties are not allowed ('Matcher' was unexpected)",
                    rule=TargetGroupHealthCheckProtocolRestrictions(),
                    validator="additionalProperties",
                    path=deque(["Matcher"]),
                    schema_path=deque(
                        ["then", "allOf", 0, "else", "properties", "Matcher", "then"]
                    ),
                )
            ],
        ),
        (
            {"HealthCheckProtocol": "TCP", "Matcher": {"GrpcCode": "12"}},
            [
                ValidationError(
                    "Additional properties are not allowed ('Matcher' was unexpected)",
                    rule=TargetGroupHealthCheckProtocolRestrictions(),
                    validator="additionalProperties",
                    path=deque(["Matcher"]),
                    schema_path=deque(
                        ["then", "allOf", 0, "else", "properties", "Matcher", "then"]
                    ),
                )
            ],
        ),
        (
            {"HealthCheckProtocol": "TCP", "ProtocolVersion": "HTTP1"},
            [
                ValidationError(
                    "Additional properties are not allowed ('ProtocolVersion' was unexpected)",
                    rule=TargetGroupHealthCheckProtocolRestrictions(),
                    validator="additionalProperties",
                    path=deque(["ProtocolVersion"]),
                    schema_path=deque(
                        ["then", "allOf", 0, "else", "properties", "ProtocolVersion"]
                    ),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
