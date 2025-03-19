"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.iam.ResourcePolicyResourceArn import (
    ResourcePolicyResourceArn,
)


@pytest.fixture(scope="module")
def rule():
    rule = ResourcePolicyResourceArn()
    yield rule


@pytest.mark.parametrize(
    "name,instance,path, expected",
    [
        (
            "Not a string",
            {},
            {"cfn_path": deque(["Resources", "AWS::S3::BucketPolicy", "Properties"])},
            [],
        ),
        (
            "Not long enough cfn path",
            "bad",
            {"cfn_path": deque(["Resources"])},
            [],
        ),
        (
            "Valid S3 ARN",
            "arn:aws:s3:::amzn-s3-demo-bucket",
            {"cfn_path": deque(["Resources", "AWS::S3::BucketPolicy", "Properties"])},
            [],
        ),
        (
            "Valid S3 ARN for objects",
            "arn:aws:s3:::amzn-s3-demo-bucket/*",
            {"cfn_path": deque(["Resources", "AWS::S3::BucketPolicy", "Properties"])},
            [],
        ),
        (
            "Invalid S3 resource ARN",
            "*",
            {"cfn_path": deque(["Resources", "AWS::S3::BucketPolicy", "Properties"])},
            [
                ValidationError(
                    (
                        "'*' does not match "
                        "'^arn:aws[A-Za-z\\\\-]*?:[^:]+:[^:]*(:(?:\\\\d{12}|\\\\*|aws)?:.+|)$'"
                    ),
                    rule=ResourcePolicyResourceArn(),
                )
            ],
        ),
        (
            "Invalid S3 resource ARN",
            "arn:aws*",
            {"cfn_path": deque(["Resources", "AWS::S3::BucketPolicy", "Properties"])},
            [
                ValidationError(
                    (
                        "'arn:aws*' does not match "
                        "'^arn:aws[A-Za-z\\\\-]*?:[^:]+:[^:]*(:(?:\\\\d{12}|\\\\*|aws)?:.+|)$'"
                    ),
                    rule=ResourcePolicyResourceArn(),
                )
            ],
        ),
        (
            "Valid SQS policy ARNs",
            "arn:aws:sqs:us-east-2:444455556666:queue1",
            {"cfn_path": deque(["Resources", "AWS::SQS::QueuePolicy", "Properties"])},
            [],
        ),
        (
            "Valid SQS policy ARNs",
            "*",
            {"cfn_path": deque(["Resources", "AWS::SQS::QueuePolicy", "Properties"])},
            [],
        ),
        (
            "Invalid SQS resource ARN",
            "arn:aws*",
            {"cfn_path": deque(["Resources", "AWS::SQS::QueuePolicy", "Properties"])},
            [
                ValidationError(
                    (
                        "'arn:aws*' does not match "
                        "'^(arn:aws[A-Za-z\\\\-]*?:[^:]+:[^:]*(:(?:\\\\d{12}|\\\\*|aws)?:.+|)|\\\\*)$'"
                    ),
                    rule=ResourcePolicyResourceArn(),
                )
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate(name, instance, path, expected, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))

    assert errors == expected, f"For test {name!r} got {errors!r}"
