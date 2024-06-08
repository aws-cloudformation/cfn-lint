"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.EventSourceMappingEventSourceArnSqsExclusive import (
    EventSourceMappingEventSourceArnSqsExclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = EventSourceMappingEventSourceArnSqsExclusive()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "EventSourceArn": "arn:aws:sqs:us-east-1:123456789012:sqs-arn",
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "EventSourceArn": "arn:aws:sqs:us-east-1:123456789012:sqs-arn",
                "StartingPosition": "1",
            },
            [
                ValidationError(
                    "Additional properties are not allowed ('StartingPosition')",
                    rule=EventSourceMappingEventSourceArnSqsExclusive(),
                    path=deque(["StartingPosition"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "StartingPosition"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
