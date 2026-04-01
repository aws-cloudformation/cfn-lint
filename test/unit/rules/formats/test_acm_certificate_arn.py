"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.AcmCertificateArn import AcmCertificateArn


@pytest.fixture(scope="module")
def rule():
    rule = AcmCertificateArn()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid ACM certificate ARN",
            "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012",
            True,
        ),
        (
            "Valid ACM certificate ARN cn",
            "arn:aws-cn:acm:cn-north-1:123456789012:certificate/abcdef",
            True,
        ),
        (
            "Invalid not ACM ARN",
            "arn:aws:iam::123456789012:role/test-role",
            False,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
