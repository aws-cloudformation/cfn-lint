"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.formats.LambdaFunctionName import LambdaFunctionName


@pytest.fixture(scope="module")
def rule():
    rule = LambdaFunctionName()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid function name",
            "my-function",
            True,
        ),
        (
            "Valid function name with underscores",
            "my_function_v2",
            True,
        ),
        (
            "Invalid has spaces",
            "my function",
            False,
        ),
        (
            "Invalid ARN should not match",
            "arn:aws:lambda:us-east-1:123456789012:function:my-func",
            False,
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"
