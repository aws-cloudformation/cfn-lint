"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError

# ruff: noqa: E501
from cfnlint.rules.resources.elasticloadbalancingv2.TargetGroupTargetTypeRestrictions import (
    TargetGroupTargetTypeRestrictions,
)


@pytest.fixture(scope="module")
def rule():
    rule = TargetGroupTargetTypeRestrictions()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"TargetType": "lambda"},
            [],
        ),
        (
            {"TargetType": "ip", "Port": "", "Protocol": "", "VpcId": ""},
            [],
        ),
        (
            [],
            [],
        ),
        (
            {"TargetType": "lambda"},
            [],
        ),
        (
            {"TargetType": "lambda", "Port": "443"},
            [
                ValidationError(
                    "Additional properties are not allowed ('Port' was unexpected)",
                    rule=TargetGroupTargetTypeRestrictions(),
                    path=deque(["Port"]),
                    validator="additionalProperties",
                    schema_path=deque(["then", "then", "properties", "Port"]),
                )
            ],
        ),
        (
            {
                "TargetType": "ip",
            },
            [
                ValidationError(
                    "'Port' is a required property",
                    rule=TargetGroupTargetTypeRestrictions(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "else", "required"]),
                ),
                ValidationError(
                    "'Protocol' is a required property",
                    rule=TargetGroupTargetTypeRestrictions(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "else", "required"]),
                ),
                ValidationError(
                    "'VpcId' is a required property",
                    rule=TargetGroupTargetTypeRestrictions(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "else", "required"]),
                ),
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
