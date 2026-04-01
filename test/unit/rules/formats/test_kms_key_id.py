"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.KmsKeyId import KmsKeyId


@pytest.fixture(scope="module")
def rule():
    rule = KmsKeyId()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid UUID key ID",
            "1234abcd-12ab-34cd-56ef-1234567890ab",
            True,
        ),
        (
            "Valid multi-region key ID",
            "mrk-1234567890abcdef1234567890abcdef",
            True,
        ),
        (
            "Valid alias",
            "alias/my-key",
            True,
        ),
        (
            "Invalid ARN should not match",
            "arn:aws:kms:us-east-1:123456789012:key/1234abcd",
            False,
        ),
        (
            "Invalid random string",
            "not-a-key-id",
            False,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
