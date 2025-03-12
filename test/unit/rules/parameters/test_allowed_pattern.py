"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.parameters.AllowedPattern import AllowedPattern


@pytest.fixture(scope="module")
def rule():
    rule = AllowedPattern()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {},
            [],
        ),
        (
            "^foo$",
            [],
        ),
        (
            "^abc|def)$",
            [
                ValidationError(
                    (
                        "'^abc|def)$' could not be "
                        "compiled (unbalanced parenthesis "
                        "at position 8)"
                    ),
                    rule=AllowedPattern(),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
