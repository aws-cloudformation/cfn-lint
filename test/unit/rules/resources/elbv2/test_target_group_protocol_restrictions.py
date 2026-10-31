"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError

# ruff: noqa: E501
from cfnlint.rules.resources.elasticloadbalancingv2.TargetGroupProtocolRestrictions import (
    TargetGroupProtocolRestrictions,
)


@pytest.fixture(scope="module")
def rule():
    rule = TargetGroupProtocolRestrictions()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Protocol": "GENEVE", "Port": 6081},
            [],
        ),
        (
            {"Protocol": "HTTPS", "Matcher": {}},
            [],
        ),
        (
            {"Protocol": {}, "Port": 6081},
            [],
        ),
        (
            [],
            [],
        ),
        (
            {"Protocol": "GENEVE", "Port": 6082},
            [
                ValidationError(
                    "6082 is not one of [6081, '6081']",
                    rule=TargetGroupProtocolRestrictions(),
                    path=deque(["Port"]),
                    validator="enum",
                    schema_path=deque(
                        ["then", "allOf", 0, "then", "properties", "Port", "enum"]
                    ),
                )
            ],
        ),
        (
            {"Protocol": "TCP", "ProtocolVersion": "HTTP1"},
            [
                ValidationError(
                    "Additional properties are not allowed ('ProtocolVersion' "
                    "was unexpected)",
                    rule=TargetGroupProtocolRestrictions(),
                    path=deque(["ProtocolVersion"]),
                    validator="additionalProperties",
                    schema_path=deque(
                        ["then", "allOf", 1, "then", "properties", "ProtocolVersion"]
                    ),
                )
            ],
        ),
        (
            {"Protocol": "UDP", "ProtocolVersion": "HTTP1"},
            [
                ValidationError(
                    "Additional properties are not allowed ('ProtocolVersion' "
                    "was unexpected)",
                    rule=TargetGroupProtocolRestrictions(),
                    path=deque(["ProtocolVersion"]),
                    validator="additionalProperties",
                    schema_path=deque(
                        ["then", "allOf", 1, "then", "properties", "ProtocolVersion"]
                    ),
                )
            ],
        ),
        (
            {"Protocol": "TLS", "ProtocolVersion": "HTTP1"},
            [
                ValidationError(
                    "Additional properties are not allowed ('ProtocolVersion' "
                    "was unexpected)",
                    rule=TargetGroupProtocolRestrictions(),
                    path=deque(["ProtocolVersion"]),
                    validator="additionalProperties",
                    schema_path=deque(
                        ["then", "allOf", 1, "then", "properties", "ProtocolVersion"]
                    ),
                )
            ],
        ),
        (
            {"Protocol": "TCP_UDP", "ProtocolVersion": "HTTP1"},
            [
                ValidationError(
                    "Additional properties are not allowed ('ProtocolVersion' "
                    "was unexpected)",
                    rule=TargetGroupProtocolRestrictions(),
                    path=deque(["ProtocolVersion"]),
                    validator="additionalProperties",
                    schema_path=deque(
                        ["then", "allOf", 1, "then", "properties", "ProtocolVersion"]
                    ),
                )
            ],
        ),
        (
            {"Protocol": "GENEVE", "Port": 6081, "ProtocolVersion": "HTTP1"},
            [
                ValidationError(
                    "Additional properties are not allowed ('ProtocolVersion' "
                    "was unexpected)",
                    rule=TargetGroupProtocolRestrictions(),
                    path=deque(["ProtocolVersion"]),
                    validator="additionalProperties",
                    schema_path=deque(
                        ["then", "allOf", 1, "then", "properties", "ProtocolVersion"]
                    ),
                )
            ],
        ),
        (
            {"Protocol": "HTTP", "ProtocolVersion": "HTTP1"},
            [],
        ),
        (
            {"Protocol": "HTTPS", "ProtocolVersion": "HTTP2"},
            [],
        ),
        (
            {"Protocol": {}, "ProtocolVersion": "HTTP1"},
            [],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
