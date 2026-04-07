"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.SnsTopicArn import SnsTopicArn


@pytest.fixture(scope="module")
def rule():
    rule = SnsTopicArn()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid SNS topic ARN",
            "arn:aws:sns:us-east-1:123456789012:my-topic",
            True,
        ),
        (
            "Valid SNS topic ARN gov",
            "arn:aws-us-gov:sns:us-gov-west-1:123456789012:my-topic",
            True,
        ),
        (
            "Invalid not SNS ARN",
            "arn:aws:iam::123456789012:role/test-role",
            False,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
