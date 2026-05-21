"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.S3BucketNameLowerCase import S3BucketNameLowerCase


@pytest.fixture(scope="module")
def rule():
    rule = S3BucketNameLowerCase()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid lowercase bucket name",
            "my-bucket-name",
            True,
        ),
        (
            "Valid lowercase with dots",
            "my.bucket.name",
            True,
        ),
        (
            "Invalid uppercase letters",
            "My-Bucket",
            False,
        ),
        (
            "Invalid all uppercase",
            "MY-BUCKET",
            False,
        ),
        (
            "Not a string",
            123,
            True,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
