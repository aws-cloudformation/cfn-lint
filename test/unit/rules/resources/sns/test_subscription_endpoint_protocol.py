"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.rules.functions.GetAtt import GetAtt
from cfnlint.rules.functions.GetAttFormat import GetAttFormat
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.sns.SubscriptionEndpointProtocol import (
    SubscriptionEndpointProtocol,
)

_getatt = GetAtt()
_getatt.child_rules["E1040"] = GetAttFormat()


@pytest.fixture(scope="module")
def rule():
    return SubscriptionEndpointProtocol()


_template = {
    "Resources": {
        "Queue": {"Type": "AWS::SQS::Queue"},
        "Function": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Runtime": "python3.12",
                "Handler": "index.handler",
                "Code": {"ZipFile": "def handler(event, context): pass"},
                "Role": "arn:aws:iam::123456789012:role/my-role",
            },
        },
        "Topic": {"Type": "AWS::SNS::Topic"},
        "Subscription": {
            "Type": "AWS::SNS::Subscription",
            "Properties": {
                "TopicArn": {"Ref": "Topic"},
                "Protocol": "sqs",
                "Endpoint": {"Fn::GetAtt": ["Queue", "Arn"]},
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,validators,expected_num_errs",
    [
        # sqs + Queue Arn — valid
        (
            _template,
            deque(["Resources", "Subscription", "Properties"]),
            {"fn_getatt": _getatt.fn_getatt},
            0,
        ),
        # lambda + Function Arn — valid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Subscription": {
                        "Type": "AWS::SNS::Subscription",
                        "Properties": {
                            "TopicArn": {"Ref": "Topic"},
                            "Protocol": "lambda",
                            "Endpoint": {"Fn::GetAtt": ["Function", "Arn"]},
                        },
                    },
                },
            },
            deque(["Resources", "Subscription", "Properties"]),
            {"fn_getatt": _getatt.fn_getatt},
            0,
        ),
        # sqs + Function Arn — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Subscription": {
                        "Type": "AWS::SNS::Subscription",
                        "Properties": {
                            "TopicArn": {"Ref": "Topic"},
                            "Protocol": "sqs",
                            "Endpoint": {"Fn::GetAtt": ["Function", "Arn"]},
                        },
                    },
                },
            },
            deque(["Resources", "Subscription", "Properties"]),
            {"fn_getatt": _getatt.fn_getatt},
            1,
        ),
        # lambda + Queue Arn — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Subscription": {
                        "Type": "AWS::SNS::Subscription",
                        "Properties": {
                            "TopicArn": {"Ref": "Topic"},
                            "Protocol": "lambda",
                            "Endpoint": {"Fn::GetAtt": ["Queue", "Arn"]},
                        },
                    },
                },
            },
            deque(["Resources", "Subscription", "Properties"]),
            {"fn_getatt": _getatt.fn_getatt},
            1,
        ),
        # http — no error
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Subscription": {
                        "Type": "AWS::SNS::Subscription",
                        "Properties": {
                            "TopicArn": {"Ref": "Topic"},
                            "Protocol": "http",
                            "Endpoint": "http://example.com",
                        },
                    },
                },
            },
            deque(["Resources", "Subscription", "Properties"]),
            {"fn_getatt": _getatt.fn_getatt},
            0,
        ),
    ],
    indirect=["template", "validators"],
)
def test_validate(template, start_path, expected_num_errs, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert len(errs) == expected_num_errs, (
            f"Expected {expected_num_errs} got {errs}"
        )
