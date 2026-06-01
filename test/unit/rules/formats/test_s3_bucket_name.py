"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.S3BucketName import S3BucketName


@pytest.fixture(scope="module")
def rule():
    rule = S3BucketName()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid bucket name",
            "my-bucket-name",
            True,
        ),
        (
            "Valid bucket name with dots",
            "my.bucket.name",
            True,
        ),
        (
            "Valid minimum length",
            "abc",
            True,
        ),
        (
            "Invalid uppercase",
            "My-Bucket",
            False,
        ),
        (
            "Invalid too short",
            "ab",
            False,
        ),
        (
            "Invalid single char",
            "a",
            False,
        ),
        (
            "Invalid consecutive dots",
            "my..bucket",
            False,
        ),
        (
            "Invalid dot dash adjacent",
            "my.-bucket",
            False,
        ),
        (
            "Invalid starts with dot",
            ".my-bucket",
            False,
        ),
        (
            "Invalid ends with dash",
            "my-bucket-",
            False,
        ),
        (
            "Invalid too long",
            "a" * 64,
            False,
        ),
        (
            "Valid max length",
            "a" * 63,
            True,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
