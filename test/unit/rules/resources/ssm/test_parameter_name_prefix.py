"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ssm.ParameterNamePrefix import ParameterNamePrefix


@pytest.fixture(scope="module")
def rule():
    rule = ParameterNamePrefix()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        ("/my/parameter/name", []),
        ("/production/db/password", []),
        ("myParameter", []),
        ("my.parameter", []),
        ("my-parameter", []),
        ("/my/nested/deep/param", []),
        (
            "/aws/service/ami-amazon-linux-latest",
            [
                ValidationError(
                    "'/aws/service/ami-amazon-linux-latest' does not match "
                    "the recommended pattern. Parameter names beginning with "
                    "'aws' or 'ssm' are reserved and may not be available "
                    "for all users."
                ),
            ],
        ),
        (
            "/ssm/managed/instance",
            [
                ValidationError(
                    "'/ssm/managed/instance' does not match "
                    "the recommended pattern. Parameter names beginning with "
                    "'aws' or 'ssm' are reserved and may not be available "
                    "for all users."
                ),
            ],
        ),
        (
            "aws-param",
            [
                ValidationError(
                    "'aws-param' does not match "
                    "the recommended pattern. Parameter names beginning with "
                    "'aws' or 'ssm' are reserved and may not be available "
                    "for all users."
                ),
            ],
        ),
        ([], []),
        ({}, []),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
