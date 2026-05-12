"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.LambdaFunctionAwsLayer import LambdaFunctionAwsLayer


@pytest.fixture(scope="module")
def rule():
    rule = LambdaFunctionAwsLayer()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            "arn:aws:lambda:us-east-1:123456789012:layer:my-layer:1",
            [],
        ),
        (
            "arn:aws:lambda:::awslayer:mainline_prerelease",
            [
                ValidationError(
                    "'arn:aws:lambda:::awslayer:mainline_prerelease' "
                    "uses the 'awslayer' format which "
                    "may not be available",
                    rule=LambdaFunctionAwsLayer(),
                    schema_path=deque(["pattern"]),
                    validator="pattern",
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
