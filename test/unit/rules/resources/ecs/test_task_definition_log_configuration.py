"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ecs.LogConfiguration import LogConfiguration


@pytest.fixture(scope="module")
def rule():
    rule = LogConfiguration()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "LogDriver": "awslogs",
                "Options": {
                    "awslogs-group": "foo",
                    "awslogs-region": "us-east-1",
                },
            },
            [],
        ),
        (
            {
                "LogDriver": "awslogs",
                "Options": {
                    "awslogs-group": "foo",
                    "awslogs-region": {"Ref": "AWS::Region"},
                },
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "LogDriver": "awslogs",
            },
            [
                ValidationError(
                    "'Options' is a required property",
                    rule=LogConfiguration(),
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
