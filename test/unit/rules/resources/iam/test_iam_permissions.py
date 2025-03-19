"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.iam.Permissions import Permissions


@pytest.fixture(scope="module")
def rule():
    rule = Permissions()
    yield rule


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid string",
            "s3:GetObject",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "Valid list",
            ["s3:GetObject"],
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "Invalid string",
            "s3:Foo",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [
                ValidationError(
                    "'foo' is not one of ['getobject', 'listaccesspoints']",
                    rule=Permissions(),
                )
            ],
        ),
        (
            "Invalid list",
            ["s3:Foo"],
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [
                ValidationError(
                    "'foo' is not one of ['getobject', 'listaccesspoints']",
                    rule=Permissions(),
                )
            ],
        ),
        (
            "Valid astrisk for permission",
            ["s3:*"],
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "Valid all astrisk",
            ["*"],
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "Valid string with ending astrisk",
            "s3:Get*",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "Valid string with starting astrisk",
            "s3:*Object",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "Invalid list",
            ["s3:Foo"],
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [
                ValidationError(
                    "'foo' is not one of ['getobject', 'listaccesspoints']",
                    rule=Permissions(),
                )
            ],
        ),
        (
            "Invalid string with ending astrisk",
            "s3:Foo*",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [
                ValidationError(
                    "'foo*' is not one of ['getobject', 'listaccesspoints']",
                    rule=Permissions(),
                )
            ],
        ),
        (
            "Invalid string with starting astrisk",
            "s3:*Foo",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [
                ValidationError(
                    "'*foo' is not one of ['getobject', 'listaccesspoints']",
                    rule=Permissions(),
                )
            ],
        ),
        (
            "Invalid service",
            "foo:Bar",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [ValidationError("'foo' is not one of ['iam', 's3']", rule=Permissions())],
        ),
        (
            "Empty string",
            "",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [
                ValidationError(
                    (
                        "'' is not a valid action. Must be "
                        "of the form service:action or '*'"
                    ),
                    rule=Permissions(),
                )
            ],
        ),
        (
            "A function",
            {"Ref": "MyParameter"},
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "asterisk in the middle",
            "iam:*Tags",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "multiple asterisks good",
            "iam:*Group*",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "multiple asterisks bad",
            "iam:*ec2*",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [
                ValidationError(
                    "'*ec2*' is not one of ['tagrole', 'creategroup', 'listgrouptags']",
                    rule=Permissions(),
                )
            ],
        ),
        (
            "question mark is bad",
            "iam:Tag?",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [
                ValidationError(
                    "'tag?' is not one of ['tagrole', 'creategroup', 'listgrouptags']",
                    rule=Permissions(),
                )
            ],
        ),
        (
            "question mark is good",
            "iam:TagRol?",
            {"cfn_path": deque(["Resources", "AWS::IAM::ManagedPolicy", "Properties"])},
            [],
        ),
        (
            "valid s3 bucket action",
            "s3:getobject",
            {"cfn_path": deque(["Resources", "AWS::S3::BucketPolicy", "Properties"])},
            [],
        ),
        (
            "invalid s3 bucket action",
            "iam:tagrole",
            {"cfn_path": deque(["Resources", "AWS::S3::BucketPolicy", "Properties"])},
            [ValidationError("'iam' is not one of ['s3']", rule=Permissions())],
        ),
        (
            "invalid s3 bucket action bucket short path",
            "iam:tagrole",
            {"cfn_path": deque(["Resources"])},
            [],
        ),
        (
            "invalid s3 bucket action",
            "iam:tagrole",
            {"cfn_path": deque(["Resources", "AWS::KMS::KeyPolicy", "Properties"])},
            [],
        ),
    ],
    indirect=["path"],
)
def test_permissions(name, instance, expected, rule, validator):

    rule._service_map = {
        "iam": {
            "Actions": {
                "tagrole": {"Resources": ["role"]},
                "creategroup": {"Resources": ["group"]},
                "listgrouptags": {"Resources": ["group"]},
            },
            "Resources": {
                "role": {
                    "ARNFormats": ["arn:${Partition}:iam::${Account}:role/.*"],
                    "ConditionKeys": [
                        "aws:ResourceTag/${TagKey}",
                        "iam:ResourceTag/${TagKey}",
                    ],
                },
                "group": {"ARNFormats": ["arn:${Partition}:iam::${Account}:group/.*"]},
            },
        },
        "s3": {
            "Actions": {
                "getobject": {"Resources": ["Object"]},
                "listaccesspoints": {},
            },
            "Resources": {
                "object": {"ARNFormats": ["arn:${Partition}:s3:::.*"]},
            },
        },
    }

    errors = list(rule.validate(validator, {}, instance, {}))

    assert errors == expected, f"Test {name!r} got {errors!r}"
