"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.iam.PolicyVersion import PolicyVersion


@pytest.fixture(scope="module")
def rule():
    rule = PolicyVersion()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        ("Valid version", "2012-10-17", []),
        (
            "Invalid version",
            "2008-10-17",
            [
                ValidationError(
                    "IAM Policy Version should be updated to '2012-10-17'",
                    rule=PolicyVersion(),
                ),
            ],
        ),
        ("No error on invalid structure", {}, []),
    ],
)
def test_policy_version(name, instance, expected, rule, validator):
    errors = list(rule.validate(validator, {}, instance, {}))
    assert errors == expected, f"Test {name!r} got {errors!r}"
