"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.PermissionSourceAccount import PermissionSourceAccount


@pytest.fixture(scope="module")
def rule():
    rule = PermissionSourceAccount()
    yield rule


@pytest.fixture
def template():
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
        },
        "Resources": {
            "Bucket": {"Type": "AWS::S3::Bucket"},
            "SQS": {"Type": "AWS::SQS::Queue"},
        },
    }


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "SourceArn": "arn:aws:s3:::bucket_name",
                "SourceAccount": "123456789012",
            },
            [],
        ),
        (
            {},
            [],
        ),
        (
            [],
            [],
        ),
        (
            {
                "SourceArn": [],
            },
            [],
        ),
        (
            {
                "SourceArn": "arn:aws:s3:::bucket_name",
            },
            [
                ValidationError(
                    "'SourceAccount' is a required property",
                    validator="required",
                    rule=PermissionSourceAccount(),
                )
            ],
        ),
        (
            {
                "SourceArn": "arn:aws:sqs:us-east-1:123456789012:queue",
            },
            [],
        ),
        (
            {
                "SourceArn": {
                    "Fn::Sub": (
                        "arn:${AWS::Partition}:sqs:"
                        "${AWS::Region}:${AWS::AccountId}:queue"
                    )
                },
            },
            [],
        ),
        (
            {
                "SourceArn": {"Fn::Sub": "arn:${AWS::Partition}:s3:::bucket"},
            },
            [],
        ),
        (
            {
                "SourceArn": {"Fn::GetAtt": ["Bucket", "Arn"]},
                "SourceAccount": {"Ref": "AWS::AccountId"},
            },
            [],
        ),
        (
            {
                "SourceArn": {"Fn::GetAtt": ["Bucket", "Arn"]},
            },
            [
                ValidationError(
                    "'SourceAccount' is a required property",
                    validator="required",
                    rule=PermissionSourceAccount(),
                )
            ],
        ),
        (
            {
                "SourceArn": {"Fn::GetAtt": ["SQS", "Arn"]},
                "SourceAccount": {"Ref": "AWS::AccountId"},
            },
            [],
        ),
        (
            {
                "SourceArn": {"Fn::GetAtt": ["SQS", "Arn"]},
            },
            [],
        ),
        (
            {
                "SourceArn": {"Ref": "Foo"},
            },
            [],
        ),
        (
            {
                "SourceArn": {
                    "Fn::If": [
                        "IsUsEast1",
                        {"Fn::GetAtt": ["Bucket", "Arn"]},
                        {"Fn::GetAtt": ["SQS", "Arn"]},
                    ]
                },
                "SourceAccount": {
                    "Fn::If": [
                        "IsUsEast1",
                        {"Ref": "AWS::AccountId"},
                        {"Ref": "AWS::NoValue"},
                    ]
                },
            },
            [],
        ),
        (
            {
                "SourceArn": {
                    "Fn::If": [
                        "IsUsEast1",
                        {"Fn::GetAtt": ["Bucket", "Arn"]},
                        {"Fn::GetAtt": ["SQS", "Arn"]},
                    ]
                },
                "SourceAccount": {
                    "Fn::If": [
                        "IsUsEast1",
                        {"Ref": "AWS::NoValue"},
                        {"Ref": "AWS::AccountId"},
                    ]
                },
            },
            [
                ValidationError(
                    "'SourceAccount' is a required property",
                    validator="required",
                    rule=PermissionSourceAccount(),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
