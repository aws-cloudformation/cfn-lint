"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.rules.RuleCondition import RuleCondition


@pytest.fixture(scope="module")
def rule():
    rule = RuleCondition()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "boolean is okay",
            True,
            [],
        ),
        (
            "wrong type",
            [],
            [
                ValidationError(
                    "[] is not of type 'boolean'",
                    validator="type",
                    schema_path=deque(["type"]),
                    rule=RuleCondition(),
                )
            ],
        ),
        (
            "functions are okay",
            {"Fn::Equals": ["a", "b"]},
            [],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, {}, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
