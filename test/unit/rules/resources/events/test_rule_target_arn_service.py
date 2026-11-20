"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

import pytest

from cfnlint.api import ManualArgs, lint_file
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.events.RuleTargetArnService import RuleTargetArnService


@pytest.fixture
def rule():
    rule = RuleTargetArnService()
    yield rule


_resources = {
    "Role": {"Type": "AWS::IAM::Role"},
    "Function": {"Type": "AWS::Lambda::Function"},
    "Topic": {"Type": "AWS::SNS::Topic"},
    "Queue": {"Type": "AWS::SQS::Queue"},
    "StateMachine": {"Type": "AWS::StepFunctions::StateMachine"},
    "Bucket": {"Type": "AWS::S3::Bucket"},
    "Stack": {"Type": "AWS::CloudFormation::Stack"},
    "Custom": {"Type": "Custom::Lookup"},
    "Product": {"Type": "AWS::ServiceCatalog::CloudFormationProvisionedProduct"},
    "ThirdParty": {"Type": "MyOrg::Some::Thing"},
}


def _template(targets, conditions=None):
    template = {
        "Parameters": {"TargetArn": {"Type": "String"}},
        "Resources": {
            **_resources,
            "Rule": {
                "Type": "AWS::Events::Rule",
                "Properties": {"Targets": targets},
            },
        },
    }
    if conditions:
        template["Conditions"] = conditions
    return template


def _err(message, path):
    return ValidationError(
        message,
        path_override=deque(["Resources", "Rule", "Properties", "Targets"] + path),
        rule=RuleTargetArnService(),
    )


_role_message = (
    "Resource 'Role' of type 'AWS::IAM::Role' is not a "
    "supported target for an EventBridge rule"
)


@pytest.mark.parametrize(
    "name,template,expected",
    [
        (
            "Supported resources by Ref and GetAtt",
            _template(
                [
                    {"Id": "1", "Arn": {"Fn::GetAtt": ["Function", "Arn"]}},
                    {"Id": "2", "Arn": {"Ref": "Topic"}},
                    {"Id": "3", "Arn": {"Fn::GetAtt": "Queue.Arn"}},
                    {"Id": "4", "Arn": {"Ref": "StateMachine"}},
                    {"Id": "5", "Arn": {"Fn::Sub": "${Function.Arn}"}},
                ]
            ),
            [],
        ),
        (
            "Supported literal and Sub ARNs",
            _template(
                [
                    {
                        "Id": "1",
                        "Arn": "arn:aws:lambda:us-east-1:123456789012:function:f",
                    },
                    {
                        "Id": "2",
                        "Arn": {
                            "Fn::Sub": (
                                "arn:${AWS::Partition}:events:${AWS::Region}:"
                                "${AWS::AccountId}:event-bus/default"
                            )
                        },
                    },
                    {
                        "Id": "3",
                        "Arn": "arn:aws-us-gov:ssm-incidents::123456789012:x/y",
                    },
                ]
            ),
            [],
        ),
        (
            "Values that can't be resolved are skipped",
            _template(
                [
                    {"Id": "1", "Arn": {"Ref": "TargetArn"}},
                    {"Id": "2", "Arn": {"Fn::ImportValue": "Shared"}},
                    {"Id": "3", "Arn": {"Fn::GetAtt": ["Stack", "Outputs.Arn"]}},
                    {"Id": "4", "Arn": {"Fn::GetAtt": ["Custom", "Arn"]}},
                    {"Id": "5", "Arn": {"Fn::GetAtt": ["ThirdParty", "Arn"]}},
                    {"Id": "6", "Arn": {"Ref": "Missing"}},
                    {"Id": "7", "Arn": {"Fn::GetAtt": []}},
                    {"Id": "8", "Arn": {"Fn::GetAtt": {"Ref": "Role"}}},
                    {"Id": "9", "Arn": {"Ref": ["Role"]}},
                    {
                        "Id": "10",
                        "Arn": {"Fn::Join": [":", ["arn", "aws", "iam", "", "r"]]},
                    },
                    {"Id": "11", "Arn": {"Fn::Sub": "${Service}"}},
                    {
                        "Id": "12",
                        "Arn": {
                            "Fn::Sub": [
                                "${Role}",
                                {"Role": {"Ref": "TargetArn"}},
                            ]
                        },
                    },
                    {
                        "Id": "13",
                        "Arn": {
                            "Fn::Sub": [
                                "arn:${AWS::Partition}:${Service}:::x",
                                {"Service": {"Ref": "TargetArn"}},
                            ]
                        },
                    },
                    {"Id": "14", "Arn": {"Fn::Sub": {"Ref": "TargetArn"}}},
                    {"Id": "15", "Arn": "not-an-arn"},
                    {"Id": "16", "Arn": "arn:aws::us-east-1:123456789012:x"},
                    {"Id": "17", "Arn": ["arn:aws:iam::123456789012:role/r"]},
                    {"Id": "18"},
                    {"Id": "19", "Arn": {"Ref": "AWS::NoValue"}},
                    {
                        "Id": "20",
                        "Arn": {"Fn::GetAtt": ["Product", "Outputs.Arn"]},
                    },
                    {"Id": "21", "Arn": {"Fn::Sub": "${Product.Outputs.Arn}"}},
                    {
                        "Id": "22",
                        "Arn": {
                            "Fn::Sub": [
                                "arn:${PartitionAndService}:${AWS::Region}:x:y",
                                {"PartitionAndService": {"Ref": "TargetArn"}},
                            ]
                        },
                    },
                ]
            ),
            [],
        ),
        (
            "IAM role by GetAtt, Ref, and Sub",
            _template(
                [
                    {"Id": "1", "Arn": {"Fn::GetAtt": ["Role", "Arn"]}},
                    {"Id": "2", "Arn": {"Fn::GetAtt": "Role.Arn"}},
                    {"Id": "3", "Arn": {"Ref": "Role"}},
                    {"Id": "4", "Arn": {"Fn::Sub": "${Role.Arn}"}},
                    {"Id": "5", "Arn": {"Fn::Sub": ["${Role.Arn}", {}]}},
                ]
            ),
            [
                _err(_role_message, [0, "Arn"]),
                _err(_role_message, [1, "Arn"]),
                _err(_role_message, [2, "Arn"]),
                _err(_role_message, [3, "Arn"]),
                _err(_role_message, [4, "Arn"]),
            ],
        ),
        (
            "Unsupported literal and Sub ARNs",
            _template(
                [
                    {"Id": "1", "Arn": "arn:aws:iam::123456789012:role/my-role"},
                    {
                        "Id": "2",
                        "Arn": {
                            "Fn::Sub": (
                                "arn:${AWS::Partition}:iam::"
                                "${AWS::AccountId}:role/my-role"
                            )
                        },
                    },
                    {
                        "Id": "3",
                        "Arn": {"Fn::Sub": ["arn:${AWS::Partition}:s3:::${B}", {}]},
                    },
                ]
            ),
            [
                _err(
                    "'iam' is not a supported service for an EventBridge rule target",
                    [0, "Arn"],
                ),
                _err(
                    "'iam' is not a supported service for an EventBridge rule target",
                    [1, "Arn"],
                ),
                _err(
                    "'s3' is not a supported service for an EventBridge rule target",
                    [2, "Arn"],
                ),
            ],
        ),
        (
            "Unsupported resource in a condition",
            _template(
                [
                    {
                        "Id": "1",
                        "Arn": {
                            "Fn::If": [
                                "IsUsEast1",
                                {"Fn::GetAtt": ["Function", "Arn"]},
                                {"Fn::GetAtt": ["Bucket", "Arn"]},
                            ]
                        },
                    },
                ],
                conditions={
                    "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]}
                },
            ),
            [
                _err(
                    (
                        "Resource 'Bucket' of type 'AWS::S3::Bucket' is not a "
                        "supported target for an EventBridge rule"
                    ),
                    [0, "Arn", "Fn::If", 2],
                ),
            ],
        ),
        (
            "Targets is not a list",
            _template({"Ref": "TargetArn"}),
            [],
        ),
    ],
    indirect=["template"],
)
def test_validate(name, template, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, deque(["Resources", "Rule", "Properties"])
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"{name}: expected {expected} got {errs}"


@pytest.mark.parametrize(
    "filename,expected",
    [
        (
            "test/fixtures/templates/good/resources/events/rule_target_arn_service.yaml",
            [],
        ),
        (
            "test/fixtures/templates/bad/resources/events/rule_target_arn_service.yaml",
            [
                ("E3730", 33),
                ("E3730", 35),
                ("E3730", 37),
                ("E3730", 39),
                ("E3730", 41),
            ],
        ),
    ],
)
def test_templates(filename, expected):
    matches = lint_file(Path(filename), ManualArgs(regions=["us-east-1"]))
    assert [(m.rule.id, m.linenumber) for m in matches] == expected
