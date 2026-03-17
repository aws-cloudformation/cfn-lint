"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import jsonpatch
import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.lmbd.PermissionSourceAccount import PermissionSourceAccount


@pytest.fixture(scope="module")
def rule():
    rule = PermissionSourceAccount()
    yield rule


_template = {
    "Conditions": {
        "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
    },
    "Resources": {
        "Bucket": {"Type": "AWS::S3::Bucket"},
        "SQS": {"Type": "AWS::SQS::Queue"},
        "Permission": {
            "Type": "AWS::Lambda::Permission",
            "Properties": {
                "SourceArn": {"Fn::GetAtt": ["Bucket", "Arn"]},
                "SourceAccount": {"Ref": "AWS::AccountId"},
            },
        },
    },
}

_error = ValidationError(
    "Validate SourceAccount is required property",
    validator="required",
    rule=PermissionSourceAccount(),
    path_override=deque([]),
    schema_path=deque(
        [
            "cfnGather",
            "schema",
            "then",
            "properties",
            "permission",
            "required",
        ]
    ),
)


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # GetAtt to S3 Bucket with SourceAccount — valid
        (
            _template,
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # GetAtt to S3 Bucket without SourceAccount — error
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "remove",
                        "path": "/Resources/Permission/Properties/SourceAccount",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [_error],
        ),
        # GetAtt to SQS (not S3) without SourceAccount — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {"Fn::GetAtt": ["SQS", "Arn"]},
                    },
                    {
                        "op": "remove",
                        "path": "/Resources/Permission/Properties/SourceAccount",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # String ARN without account ID — error
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": "arn:aws:s3:::bucket_name",
                    },
                    {
                        "op": "remove",
                        "path": "/Resources/Permission/Properties/SourceAccount",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [_error],
        ),
        # String ARN with account ID — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": "arn:aws:sqs:us-east-1:123456789012:queue",
                    },
                    {
                        "op": "remove",
                        "path": "/Resources/Permission/Properties/SourceAccount",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # String ARN with SourceAccount — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": "arn:aws:s3:::bucket_name",
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceAccount",
                        "value": "123456789012",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # No SourceArn at all — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "remove",
                        "path": "/Resources/Permission/Properties/SourceArn",
                    },
                    {
                        "op": "remove",
                        "path": "/Resources/Permission/Properties/SourceAccount",
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # Fn::If with GetAtt to Bucket/SQS, SourceAccount matches condition — valid
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {
                            "Fn::If": [
                                "IsUsEast1",
                                {"Fn::GetAtt": ["Bucket", "Arn"]},
                                {"Fn::GetAtt": ["SQS", "Arn"]},
                            ]
                        },
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceAccount",
                        "value": {
                            "Fn::If": [
                                "IsUsEast1",
                                {"Ref": "AWS::AccountId"},
                                {"Ref": "AWS::NoValue"},
                            ]
                        },
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [],
        ),
        # Fn::If with GetAtt to Bucket/SQS, SourceAccount WRONG condition — error
        (
            jsonpatch.apply_patch(
                _template,
                [
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceArn",
                        "value": {
                            "Fn::If": [
                                "IsUsEast1",
                                {"Fn::GetAtt": ["Bucket", "Arn"]},
                                {"Fn::GetAtt": ["SQS", "Arn"]},
                            ]
                        },
                    },
                    {
                        "op": "replace",
                        "path": "/Resources/Permission/Properties/SourceAccount",
                        "value": {
                            "Fn::If": [
                                "IsUsEast1",
                                {"Ref": "AWS::NoValue"},
                                {"Ref": "AWS::AccountId"},
                            ]
                        },
                    },
                ],
            ),
            deque(["Resources", "Permission", "Properties"]),
            [_error],
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
