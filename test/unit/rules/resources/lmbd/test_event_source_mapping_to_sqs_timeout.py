"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import jsonpatch
import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.EventSourceMappingToSqsTimeout import (
    EventSourceMappingToSqsTimeout,
)


@pytest.fixture(scope="module")
def rule():
    rule = EventSourceMappingToSqsTimeout()
    yield rule


_template = {
    "Parameters": {
        "BatchSize": {"Type": "String"},
    },
    "Resources": {
        "MyFifoQueue": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "VisibilityTimeout": 300,
                "MessageRetentionPeriod": 7200,
            },
        },
        "SQSBatch": {
            "Type": "AWS::Lambda::EventSourceMapping",
            "Properties": {
                "BatchSize": {"Ref": "BatchSize"},
                "Enabled": True,
                "EventSourceArn": {"Fn::GetAtt": "MyFifoQueue.Arn"},
                "FunctionName": {"Ref": "Lambda"},
            },
        },
        "Lambda": {
            "Type": "AWS::Lambda::Function",
            "Properties": {"Role": {"Fn::GetAtt": "Role.Arn"}},
        },
        "CustomResource": {
            "Type": "AWS::CloudFormation::CustomResource",
            "Properties": {"Key": {"Fn::GetAtt": "Lambda.Arn"}},
        },
    },
    "Outputs": {
        "LambdaArn": {"Value": {"Fn::GetAtt": "Lambda.Arn"}},
        "SourceMapping": {"Value": {"Ref": "SQSBatch"}},
    },
}


@pytest.mark.parametrize(
    "instance,template,path,expected",
    [
        (
            "100",
            _template,
            {"path": deque(["Resources", "Lambda", "Properties", "Timeout"])},
            [],
        ),
        (
            "a",
            _template,
            {"path": deque(["Resources", "Lambda", "Properties", "Timeout"])},
            [],
        ),
        (
            {"Ref": "AWS::Region"},
            _template,
            {"path": deque(["Resources", "Lambda", "Properties", "Timeout"])},
            [],
        ),
        (
            "100",
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "add",
                        "path": (
                            "/Resources/MyFifoQueue/" "Properties/VisibilityTimeout"
                        ),
                        "value": "300",
                    },
                ],
            ),
            {"path": deque(["Resources", "Lambda", "Properties", "Timeout"])},
            [],
        ),
        (
            "600",
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "add",
                        "path": (
                            "/Resources/MyFifoQueue/" "Properties/VisibilityTimeout"
                        ),
                        "value": {"Ref": "AWS::Region"},
                    },
                ],
            ),
            {"path": deque(["Resources", "Lambda", "Properties", "Timeout"])},
            [],
        ),
        (
            "600",
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "add",
                        "path": (
                            "/Resources/MyFifoQueue/" "Properties/VisibilityTimeout"
                        ),
                        "value": "a",
                    },
                ],
            ),
            {"path": deque(["Resources", "Lambda", "Properties", "Timeout"])},
            [],
        ),
        (
            "600",
            _template,
            {"path": deque(["Resources"])},
            [],
        ),
        (
            "600",
            _template,
            {"path": deque(["Resources", "Lambda", "Properties", "Timeout"])},
            [
                ValidationError(
                    (
                        "Queue visibility timeout (300) is less "
                        "than Function timeout (600) seconds"
                    ),
                    rule=EventSourceMappingToSqsTimeout(),
                )
            ],
        ),
    ],
    indirect=["template", "path"],
)
def test_lambda_runtime(instance, template, path, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
