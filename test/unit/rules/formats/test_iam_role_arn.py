"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.IamRoleArn import IamRoleArn


@pytest.fixture(scope="module")
def rule():
    rule = IamRoleArn()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid IAM Role arn",
            "arn:aws:iam::123456789012:role/test-role",
            True,
        ),
        (
            "Invalid Iam role Arn",
            "arn:partition:iam::123456789012:role/test-role",
            False,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
