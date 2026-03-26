"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.lmbd.EventSourceMappingSqsFifoBatchSize import (
    EventSourceMappingSqsFifoBatchSize,
)


@pytest.fixture(scope="module")
def rule():
    return EventSourceMappingSqsFifoBatchSize()


_template = {
    "Resources": {
        "FifoQueue": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "FifoQueue": True,
            },
        },
        "StandardQueue": {
            "Type": "AWS::SQS::Queue",
        },
        "Mapping": {
            "Type": "AWS::Lambda::EventSourceMapping",
            "Properties": {
                "EventSourceArn": {"Fn::GetAtt": "FifoQueue.Arn"},
                "FunctionName": {"Ref": "Function"},
                "BatchSize": 10,
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # FIFO queue with BatchSize 10 — valid
        (
            _template,
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # FIFO queue with BatchSize 100 — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "FifoQueue.Arn"},
                            "FunctionName": {"Ref": "Function"},
                            "BatchSize": 100,
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "100 is greater than the maximum of 10",
                    validator="maximum",
                    rule=EventSourceMappingSqsFifoBatchSize(),
                    path=deque(["BatchSize"]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "local",
                            "properties",
                            "BatchSize",
                            "maximum",
                        ]
                    ),
                ),
            ],
        ),
        # Standard queue with BatchSize 100 — valid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "StandardQueue.Arn"},
                            "FunctionName": {"Ref": "Function"},
                            "BatchSize": 100,
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # FIFO queue with no BatchSize — valid (default is 10)
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": {"Fn::GetAtt": "FifoQueue.Arn"},
                            "FunctionName": {"Ref": "Function"},
                        },
                    },
                },
            },
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        # Hardcoded DynamoDB stream ARN with BatchSize 100 — valid (not SQS)
        (
            {
                "Resources": {
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": (
                                "arn:aws:dynamodb:us-east-1:"
                                "123456789012:table/T/stream/2024"
                            ),
                            "FunctionName": "my-func",
                            "BatchSize": 100,
                        },
                    },
                },
            },
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
