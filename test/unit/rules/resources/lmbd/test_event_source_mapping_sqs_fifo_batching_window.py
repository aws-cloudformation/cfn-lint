"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.lmbd.EventSourceMappingSqsFifoBatchingWindow import (
    EventSourceMappingSqsFifoBatchingWindow,
)


@pytest.fixture(scope="module")
def rule():
    return EventSourceMappingSqsFifoBatchingWindow()


_queues = {
    "FifoQueue": {
        "Type": "AWS::SQS::Queue",
        "Properties": {
            "FifoQueue": True,
        },
    },
    "StandardQueue": {
        "Type": "AWS::SQS::Queue",
    },
}


def _mapping(properties):
    return {
        "Resources": {
            **_queues,
            "Mapping": {
                "Type": "AWS::Lambda::EventSourceMapping",
                "Properties": {
                    "FunctionName": "my-func",
                    **properties,
                },
            },
        },
    }


def _err(value, schema_path):
    return ValidationError(
        (
            f"{value} is greater than the maximum of 0 "
            "when the event source is an SQS FIFO queue"
        ),
        validator="maximum",
        rule=EventSourceMappingSqsFifoBatchingWindow(),
        path=deque(["MaximumBatchingWindowInSeconds"]),
        schema_path=deque(schema_path),
    )


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # FIFO queue without a batching window — valid
        (
            _mapping({"EventSourceArn": {"Fn::GetAtt": "FifoQueue.Arn"}}),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # FIFO queue with a batching window of 0 — valid
        (
            _mapping(
                {
                    "EventSourceArn": {"Fn::GetAtt": "FifoQueue.Arn"},
                    "MaximumBatchingWindowInSeconds": 0,
                }
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # FIFO queue with a batching window — invalid
        (
            _mapping(
                {
                    "EventSourceArn": {"Fn::GetAtt": "FifoQueue.Arn"},
                    "MaximumBatchingWindowInSeconds": 10,
                }
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [
                _err(
                    10,
                    [
                        "allOf",
                        0,
                        "cfnGather",
                        "schema",
                        "then",
                        "properties",
                        "local",
                        "properties",
                        "MaximumBatchingWindowInSeconds",
                        "maximum",
                    ],
                ),
            ],
        ),
        # Standard queue with a batching window — valid
        (
            _mapping(
                {
                    "EventSourceArn": {"Fn::GetAtt": "StandardQueue.Arn"},
                    "MaximumBatchingWindowInSeconds": 10,
                }
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # FIFO queue with a batching window that isn't known — valid
        (
            _mapping(
                {
                    "EventSourceArn": {"Fn::GetAtt": "FifoQueue.Arn"},
                    "MaximumBatchingWindowInSeconds": {"Ref": "Window"},
                }
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # Hardcoded FIFO queue ARN with a batching window — invalid
        (
            _mapping(
                {
                    "EventSourceArn": "arn:aws:sqs:us-east-1:123456789012:q.fifo",
                    "MaximumBatchingWindowInSeconds": 5,
                }
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [
                _err(
                    5,
                    [
                        "allOf",
                        1,
                        "then",
                        "properties",
                        "MaximumBatchingWindowInSeconds",
                        "maximum",
                    ],
                ),
            ],
        ),
        # Hardcoded standard queue ARN with a batching window — valid
        (
            _mapping(
                {
                    "EventSourceArn": "arn:aws:sqs:us-east-1:123456789012:q",
                    "MaximumBatchingWindowInSeconds": 5,
                }
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # Hardcoded Kinesis stream ARN ending in .fifo — valid (not SQS)
        (
            _mapping(
                {
                    "EventSourceArn": (
                        "arn:aws:kinesis:us-east-1:123456789012:stream/s.fifo"
                    ),
                    "MaximumBatchingWindowInSeconds": 5,
                }
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # EventSourceArn that isn't known — valid
        (
            _mapping(
                {
                    "EventSourceArn": {"Ref": "QueueArn"},
                    "MaximumBatchingWindowInSeconds": 5,
                }
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
    ],
    indirect=["template"],
)
def test_validate(template, start_path, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"Expected {expected} got {errs}"
