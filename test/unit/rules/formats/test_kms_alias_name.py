"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.KmsAliasName import KmsAliasName


@pytest.fixture(scope="module")
def rule():
    rule = KmsAliasName()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid alias",
            "alias/my-key",
            True,
        ),
        (
            "Valid aws managed alias",
            "alias/aws/s3",
            True,
        ),
        (
            "Invalid no prefix",
            "my-key",
            False,
        ),
        (
            "Invalid ARN",
            "arn:aws:kms:us-east-1:123456789012:alias/my-key",
            False,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
