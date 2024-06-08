"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.EventSourceMappingEventSourceArnStreamInclusive import (  # noqa: E501
    EventSourceMappingEventSourceArnStreamInclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = EventSourceMappingEventSourceArnStreamInclusive()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "EventSourceArn": "arn:aws:kinesis:us-east-1:123456789012:kinesis-arn",
                "StartingPosition": "1",
            },
            [],
        ),
        (
            [],  # wrong type
            [],
        ),
        (
            {
                "EventSourceArn": "arn:aws:kinesis:us-east-1:123456789012:kinesis-arn",
            },
            [
                ValidationError(
                    "'StartingPosition' is a required property",
                    rule=EventSourceMappingEventSourceArnStreamInclusive(),
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
