"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.iam.StatementResources import StatementResources


@pytest.fixture(scope="module")
def rule():
    rule = StatementResources()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "Action": "cloudformation:CreateStackSet",
                "Resource": "*",
            },
            [],
        ),
        (
            {
                "Action": ["cloudformation:CreateStackSet"],
                "Resource": ["*"],
            },
            [],
        ),
        (
            {
                "Action": ["cloudformation:CreateStack"],
                "Resource": "*",
            },
            [],
        ),
        (
            {
                "Action": "cloudformation:CreateStackSet",
                "Resource": "arn",
            },
            [
                ValidationError(
                    "'*' was expected",
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                    schema_path=deque(
                        ["then", "properties", "Resource", "then", "const"]
                    ),
                    validator="const",
                ),
            ],
        ),
        (
            {
                "Action": ["cloudformation:CreateStackSet"],
                "Resource": ["arn"],
            },
            [
                ValidationError(
                    "'*' not found in array",
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                    schema_path=deque(
                        ["then", "properties", "Resource", "else", "contains"]
                    ),
                    validator="contains",
                ),
            ],
        ),
        (
            {
                "Action": ["cloudformation:CreateStackSet"],
                "Resource": ["arn", "*"],
            },
            [],
        ),
        (
            {
                "Action": [
                    "cloudformation:CreateStackSet",
                    "cloudformation:CreateStack",
                ],
                "Resource": ["arn"],
            },
            [
                ValidationError(
                    "'*' not found in array",
                    rule=StatementResources(),
                    path=deque(["Resource"]),
                    schema_path=deque(
                        ["then", "properties", "Resource", "else", "contains"]
                    ),
                    validator="contains",
                ),
            ],
        ),
    ],
)
def test_rule(instance, expected, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))
    assert errors == expected, f"Got {errors!r}"
