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
                        ["then", "allOf", 1, "then", "properties", "Port", "enum"]
                    ),
                )
            ],
        ),
        (
            {"Protocol": "TLS", "Matcher": {}},
            [
                ValidationError(
                    "Additional properties are not allowed ('Matcher' was unexpected)",
                    rule=TargetGroupProtocolRestrictions(),
                    validator="additionalProperties",
                    path=deque(["Matcher"]),
                    schema_path=deque(
                        ["then", "allOf", 0, "else", "properties", "Matcher"]
                    ),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
