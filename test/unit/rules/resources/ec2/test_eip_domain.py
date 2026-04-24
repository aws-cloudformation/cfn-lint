"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.EipDomain import EipDomain


@pytest.fixture(scope="module")
def rule():
    rule = EipDomain()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        ("vpc", []),
        ("standard", []),
        ("VPC", []),
        ("Standard", []),
        (
            "myVpc",
            [
                ValidationError(
                    "'myVpc' is not a standard Domain value. "
                    "Non-standard values are silently converted to 'vpc'."
                ),
            ],
        ),
        (
            "vpc-0abc123",
            [
                ValidationError(
                    "'vpc-0abc123' is not a standard Domain value. "
                    "Non-standard values are silently converted to 'vpc'."
                ),
            ],
        ),
        (
            "foo",
            [
                ValidationError(
                    "'foo' is not a standard Domain value. "
                    "Non-standard values are silently converted to 'vpc'."
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
