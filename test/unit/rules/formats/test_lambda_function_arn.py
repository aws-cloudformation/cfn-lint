"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.LambdaFunctionArn import LambdaFunctionArn


@pytest.fixture(scope="module")
def rule():
    rule = LambdaFunctionArn()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid Lambda function ARN",
            "arn:aws:lambda:us-east-1:123456789012:function:my-func",
            True,
        ),
        (
            "Valid Lambda function ARN with version",
            "arn:aws:lambda:us-east-1:123456789012:function:my-func:1",
            True,
        ),
        (
            "Valid Lambda function ARN with alias",
            "arn:aws:lambda:us-east-1:123456789012:function:my-func:PROD",
            True,
        ),
        (
            "Invalid Lambda layer ARN",
            "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1",
            False,
        ),
        (
            "Invalid not Lambda ARN",
            "arn:aws:iam::123456789012:role/test-role",
            False,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
