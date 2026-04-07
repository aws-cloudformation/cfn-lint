"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import jsonpatch
import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.lmbd.PermissionPrincipal import PermissionPrincipal


@pytest.fixture(scope="module")
def rule():
    rule = PermissionPrincipal()
    yield rule


_template = {
    "Resources": {
        "Bucket": {"Type": "AWS::S3::Bucket"},
        "Topic": {"Type": "AWS::SNS::Topic"},
        "Rule": {"Type": "AWS::Events::Rule"},
        "Api": {"Type": "AWS::ApiGateway::RestApi"},
        "LogGroup": {"Type": "AWS::Logs::LogGroup"},
        "ConfigRule": {"Type": "AWS::Config::ConfigRule"},
        "UserPool": {"Type": "AWS::Cognito::UserPool"},
        "TopicRule": {"Type": "AWS::IoT::TopicRule"},
        "Permission": {
            "Type": "AWS::Lambda::Permission",
            "Properties": {
                "SourceArn": {"Fn::GetAtt": ["Bucket", "Arn"]},
                "Principal": "s3.amazonaws.com",
            },
        },
    },
}

_schema_path = deque(
    [
        "cfnGather",
        "schema",
        "then",
        "properties",
        "permission",
        "properties",
        "principal",
        "const",
    ]
)


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # S3 Bucket with correct principal — valid
        (
            _template,
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # S3 Bucket with wrong principal — error
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "sns.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [
                ValidationError(
                    "'s3.amazonaws.com' was expected",
                    validator="const",
                    rule=PermissionPrincipal(),
                    path=deque(["Principal"]),
                    schema_path=_schema_path,
                ),
            ],
        ),
        # SNS Topic with correct principal — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Ref": "Topic"},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "sns.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # SNS Topic with wrong principal — error
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Ref": "Topic"},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "s3.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [
                ValidationError(
                    "'sns.amazonaws.com' was expected",
                    validator="const",
                    rule=PermissionPrincipal(),
                    path=deque(["Principal"]),
                    schema_path=_schema_path,
                ),
            ],
        ),
        # Events Rule with correct principal — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Fn::GetAtt": ["Rule", "Arn"]},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "events.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # API Gateway with correct principal — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Ref": "Api"},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "apigateway.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # CloudWatch Logs LogGroup with correct principal — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Fn::GetAtt": ["LogGroup", "Arn"]},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "logs.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # CloudWatch Logs LogGroup with wrong principal — error
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Fn::GetAtt": ["LogGroup", "Arn"]},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "s3.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [
                ValidationError(
                    "'logs.amazonaws.com' was expected",
                    validator="const",
                    rule=PermissionPrincipal(),
                    path=deque(["Principal"]),
                    schema_path=_schema_path,
                ),
            ],
        ),
        # Config ConfigRule with correct principal — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Fn::GetAtt": ["ConfigRule", "Arn"]},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "config.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # Cognito UserPool with correct principal — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Fn::GetAtt": ["UserPool", "Arn"]},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "cognito-idp.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # IoT TopicRule with correct principal — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Fn::GetAtt": ["TopicRule", "Arn"]},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "iot.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # IoT TopicRule with wrong principal — error
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Fn::GetAtt": ["TopicRule", "Arn"]},
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "s3.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [
                ValidationError(
                    "'iot.amazonaws.com' was expected",
                    validator="const",
                    rule=PermissionPrincipal(),
                    path=deque(["Principal"]),
                    schema_path=_schema_path,
                ),
            ],
        ),
        # String SourceArn (no resource reference) — valid (skip)
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": "arn:aws:s3:::my-bucket",
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/Principal",
                        "value": "events.amazonaws.com",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # No SourceArn — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "remove",
                        "path": "/Resources/Permission/Properties/SourceArn",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # Unknown resource type (not in $lookup map) — valid (skip)
        (
            {
                "Resources": {
                    "Queue": {"Type": "AWS::SQS::Queue"},
                    "Permission": {
                        "Type": "AWS::Lambda::Permission",
                        "Properties": {
                            "SourceArn": {"Fn::GetAtt": ["Queue", "Arn"]},
                            "Principal": "anything.amazonaws.com",
                        },
                    },
                },
            },
            deque(["Resources", "Permission", "Properties"]),
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
