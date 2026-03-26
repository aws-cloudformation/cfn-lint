"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import jsonpatch
import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.lmbd.EventSourceMappingToSqsTimeout import (
    EventSourceMappingToSqsTimeout,
)


@pytest.fixture(scope="module")
def rule():
    rule = EventSourceMappingToSqsTimeout()
    yield rule


_template = {
    "Resources": {
        "Queue": {
            "Type": "AWS::SQS::Queue",
            "Properties": {
                "VisibilityTimeout": 300,
            },
        },
        "Lambda": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Timeout": 100,
                "Role": {"Fn::GetAtt": "Role.Arn"},
            },
        },
        "Mapping": {
            "Type": "AWS::Lambda::EventSourceMapping",
            "Properties": {
                "EventSourceArn": {"Fn::GetAtt": "Queue.Arn"},
                "FunctionName": {"Ref": "Lambda"},
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        (
            _template,
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Lambda/Properties/Timeout",
                        "value": 600,
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "Queue visibility timeout (300) is less "
                    "than Function timeout (600) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        ["Resources", "Queue", "Properties", "VisibilityTimeout"]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Lambda/Properties/Timeout",
                        "value": "600",
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Queue/Properties/VisibilityTimeout",
                        "value": {"Ref": "AWS::Region"},
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Mapping/Properties/EventSourceArn",
                        "value": {"Fn::GetAtt": "Lambda.Arn"},
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "remove",
                        "path": "/Resources/Lambda/Properties/Timeout",
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [],
        ),
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "remove",
                        "path": "/Resources/Queue/Properties/VisibilityTimeout",
                    },
                ],
            ),
            deque(["Resources", "Mapping", "Properties"]),
            [
                ValidationError(
                    "Queue visibility timeout (30) is less "
                    "than Function timeout (100) seconds",
                    validator="minimum",
                    rule=EventSourceMappingToSqsTimeout(),
                    path_override=deque(
                        [
                            "Resources",
                            "Queue",
                            "Properties",
                            "VisibilityTimeout",
                        ]
                    ),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "then",
                            "properties",
                            "queue",
                            "properties",
                            "VisibilityTimeout",
                            "minimum",
                        ]
                    ),
                ),
            ],
        ),
        # Hardcoded EventSourceArn — no error
        (
            {
                "Resources": {
                    "Function": {
                        "Type": "AWS::Lambda::Function",
                        "Properties": {
                            "Runtime": "python3.12",
                            "Handler": "index.handler",
                            "Code": {"ZipFile": "def handler(e, c): pass"},
                            "Role": "arn:aws:iam::123456789012:role/role",
                            "Timeout": 900,
                        },
                    },
                    "Mapping": {
                        "Type": "AWS::Lambda::EventSourceMapping",
                        "Properties": {
                            "EventSourceArn": (
                                "arn:aws:sqs:us-east-1:123456789012:my-queue"
                            ),
                            "FunctionName": {"Ref": "Function"},
                            "BatchSize": 10,
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
