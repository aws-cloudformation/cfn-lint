"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.elasticloadbalancingv2.ListenerRuleTargetGroupProtocol import (  # noqa: E501
    ListenerRuleTargetGroupProtocol,
)


@pytest.fixture(scope="module")
def rule():
    rule = ListenerRuleTargetGroupProtocol()
    yield rule


@pytest.fixture
def template():
    return {
        "Conditions": {
            "IsGeneve": {"Fn::Equals": [{"Ref": "Protocol"}, "GENEVE"]},
        },
        "Parameters": {
            "Protocol": {"Type": "String"},
        },
        "Resources": {
            "HttpTargetGroup": {
                "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
                "Properties": {
                    "Protocol": "HTTP",
                    "Port": 80,
                    "VpcId": "vpc-12345",
                },
            },
            "GeneveTargetGroup": {
                "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
                "Properties": {
                    "Protocol": "GENEVE",
                    "Port": 6081,
                    "VpcId": "vpc-12345",
                },
            },
            "NoProtocolTargetGroup": {
                "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
                "Properties": {
                    "VpcId": "vpc-12345",
                },
            },
            "CustomResource": {
                "Type": "AWS::CloudFormation::CustomResource",
            },
        },
    }


@pytest.mark.parametrize(
    "instance,expected",
    [
        # Valid: forward to HTTP target group
        (
            {
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": {"Ref": "HttpTargetGroup"},
                    }
                ],
            },
            [],
        ),
        # Valid: redirect action (no target group)
        (
            {
                "Actions": [
                    {
                        "Type": "redirect",
                        "RedirectConfig": {
                            "StatusCode": "HTTP_301",
                        },
                    }
                ],
            },
            [],
        ),
        # Valid: target group without protocol specified
        (
            {
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": {"Ref": "NoProtocolTargetGroup"},
                    }
                ],
            },
            [],
        ),
        # Valid: reference to non-TargetGroup resource (filtered out)
        (
            {
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": {"Ref": "CustomResource"},
                    }
                ],
            },
            [],
        ),
        # Valid: TargetGroupArn is a plain string ARN (not a Ref)
        (
            {
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": (
                            "arn:aws:elasticloadbalancing:"
                            "us-east-1:123456789012:"
                            "targetgroup/my-tg/abc123"
                        ),
                    }
                ],
            },
            [],
        ),
        # Invalid: forward to GENEVE target group
        (
            {
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": {"Ref": "GeneveTargetGroup"},
                    }
                ],
            },
            [
                ValidationError(
                    (
                        "TargetGroup protocol 'GENEVE' is not compatible with "
                        "ListenerRule forwarding actions. GENEVE is only supported "
                        "with Gateway Load Balancers."
                    ),
                    rule=ListenerRuleTargetGroupProtocol(),
                ),
            ],
        ),
        # Invalid: GENEVE target group via GetAtt
        (
            {
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": {
                            "Fn::GetAtt": "GeneveTargetGroup.TargetGroupArn"
                        },
                    }
                ],
            },
            [
                ValidationError(
                    (
                        "TargetGroup protocol 'GENEVE' is not compatible with "
                        "ListenerRule forwarding actions. GENEVE is only supported "
                        "with Gateway Load Balancers."
                    ),
                    rule=ListenerRuleTargetGroupProtocol(),
                ),
            ],
        ),
        # Valid: conditional TargetGroupArn where GENEVE branch matches condition
        (
            {
                "Actions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": {
                            "Fn::If": [
                                "IsGeneve",
                                {"Ref": "GeneveTargetGroup"},
                                {"Ref": "HttpTargetGroup"},
                            ]
                        },
                    }
                ],
            },
            [
                ValidationError(
                    (
                        "TargetGroup protocol 'GENEVE' is not compatible with "
                        "ListenerRule forwarding actions. GENEVE is only supported "
                        "with Gateway Load Balancers."
                    ),
                    rule=ListenerRuleTargetGroupProtocol(),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert len(errs) == len(expected), (
        f"Expected {len(expected)} errors, got {len(errs)}: {errs}"
    )
    for err, exp in zip(errs, expected):
        assert err.message == exp.message, (
            f"Expected message '{exp.message}', got '{err.message}'"
        )
