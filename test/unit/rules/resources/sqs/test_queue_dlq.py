"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.sqs.QueueDLQ import QueueDLQ


@pytest.fixture(scope="module")
def rule():
    rule = QueueDLQ()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {"FifoQueue": {"Type": "Boolean"}},
        "Conditions": {"UseFifoQueue": {"Fn::Equals": [{"Ref": "FifoQueue"}, "true"]}},
        "Resources": {
            "CustomResource": {"Type": "AWS::CloudFormation::CustomResource"},
            "FifoQueue": {
                "Type": "AWS::SQS::Queue",
                "Properties": {
                    "FifoQueue": True,
                },
            },
            "StandardQueue1": {
                "Type": "AWS::SQS::Queue",
                "Properties": {},
            },
            "StandardQueue2": {
                "Type": "AWS::SQS::Queue",
                "Properties": {
                    "FifoQueue": "false",
                },
            },
        },
    }


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "FifoQueue": True,
                "RedrivePolicy": {
                    "deadLetterTargetArn": {"Fn::GetAtt": "FifoQueue.Arn"}
                },
            },
            [],
        ),
        (
            {
                "FifoQueue": True,
                "RedrivePolicy": {
                    "deadLetterTargetArn": {"Fn::GetAtt": "CustomResource.Arn"}
                },
            },
            [],
        ),
        (
            {
                "RedrivePolicy": {
                    "deadLetterTargetArn": {"Fn::GetAtt": "StandardQueue1.Arn"}
                }
            },
            [],
        ),
        (
            {
                "RedrivePolicy": {
                    "deadLetterTargetArn": {"Fn::GetAtt": "StandardQueue2.Arn"}
                }
            },
            [],
        ),
        (
            {"RedrivePolicy": {"deadLetterTargetArn": {"Fn::GetAtt": []}}},
            [],
        ),
        (
            {
                "RedrivePolicy": {
                    "deadLetterTargetArn": {"Fn::GetAtt": "CustomResource.Arn"}
                }
            },
            [],
        ),
        (
            {
                "FifoQueue": {
                    "Fn::If": [
                        "UseFifoQueue",
                        True,
                        False,
                    ]
                },
                "RedrivePolicy": {
                    "deadLetterTargetArn": {
                        "Fn::If": [
                            "UseFifoQueue",
                            {"Fn::GetAtt": "FifoQueue.Arn"},
                            {"Fn::GetAtt": "StandardQueue1.Arn"},
                        ]
                    }
                },
            },
            [],
        ),
        (
            {
                "FifoQueue": True,
                "RedrivePolicy": {
                    "deadLetterTargetArn": {"Fn::GetAtt": "StandardQueue1.Arn"}
                },
            },
            [
                ValidationError(
                    (
                        "Source queue type 'FIFO' does not match "
                        "destination queue type 'standard'"
                    ),
                    rule=QueueDLQ(),
                    path=deque(["RedrivePolicy", "deadLetterTargetArn"]),
                )
            ],
        ),
        (
            {
                "FifoQueue": True,
                "RedrivePolicy": {
                    "deadLetterTargetArn": {"Fn::GetAtt": "StandardQueue2.Arn"}
                },
            },
            [
                ValidationError(
                    (
                        "Source queue type 'FIFO' does not match "
                        "destination queue type 'standard'"
                    ),
                    rule=QueueDLQ(),
                    path=deque(["RedrivePolicy", "deadLetterTargetArn"]),
                )
            ],
        ),
        (
            {
                "FifoQueue": "false",
                "RedrivePolicy": {
                    "deadLetterTargetArn": {"Fn::GetAtt": "FifoQueue.Arn"}
                },
            },
            [
                ValidationError(
                    (
                        "Source queue type 'standard' does not "
                        "match destination queue type 'FIFO'"
                    ),
                    rule=QueueDLQ(),
                    path=deque(["RedrivePolicy", "deadLetterTargetArn"]),
                )
            ],
        ),
        (
            {
                "FifoQueue": {
                    "Fn::If": [
                        "UseFifoQueue",
                        True,
                        False,
                    ]
                },
                "RedrivePolicy": {
                    "deadLetterTargetArn": {
                        "Fn::If": [
                            "UseFifoQueue",
                            {"Fn::GetAtt": "StandardQueue1.Arn"},
                            {"Fn::GetAtt": "FifoQueue.Arn"},
                        ]
                    }
                },
            },
            [
                ValidationError(
                    (
                        "Source queue type 'FIFO' does not match "
                        "destination queue type 'standard'"
                    ),
                    rule=QueueDLQ(),
                    path=deque(["RedrivePolicy", "deadLetterTargetArn", "Fn::If", 1]),
                ),
                ValidationError(
                    (
                        "Source queue type 'standard' does "
                        "not match destination queue type 'FIFO'"
                    ),
                    rule=QueueDLQ(),
                    path=deque(["RedrivePolicy", "deadLetterTargetArn", "Fn::If", 2]),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
