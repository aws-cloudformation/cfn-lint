"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.KmsKeyArn import KmsKeyArn


@pytest.fixture(scope="module")
def rule():
    rule = KmsKeyArn()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid KMS key ARN",
            "arn:aws:kms:us-east-1:123456789012:key/1234abcd-12ab-34cd-56ef-1234567890ab",
            True,
        ),
        (
            "Valid KMS alias ARN",
            "arn:aws:kms:us-east-1:123456789012:alias/my-key",
            True,
        ),
        (
            "Valid KMS key ARN cn partition",
            "arn:aws-cn:kms:cn-north-1:123456789012:key/1234abcd",
            True,
        ),
        (
            "Invalid not a KMS ARN",
            "arn:aws:iam::123456789012:role/test-role",
            False,
        ),
        (
            "Invalid bare key ID",
            "1234abcd-12ab-34cd-56ef-1234567890ab",
            False,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
