"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ecs.TaskDefinitionEssentialContainer import (
    TaskDefinitionEssentialContainer,
)


@pytest.fixture(scope="module")
def rule():
    rule = TaskDefinitionEssentialContainer()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            [{"Essential": True}],
            [],
        ),
        (
            [{"Essential": True}, {"Essential": False}],
            [],
        ),
        (
            {},  # wrong type
            [],
        ),
        (
            [{"Essential": {"Ref": "Essential"}}, {"Essential": False}],
            [],
        ),
        (
            [{"Essential": False}],
            [
                ValidationError(
                    "At least one essential container is required",
                    rule=TaskDefinitionEssentialContainer(),
                    path=deque([]),
                    validator="contains",
                    schema_path=deque(["contains"]),
                )
            ],
        ),
        (
            [],
            [
                ValidationError(
                    "At least one essential container is required",
                    rule=TaskDefinitionEssentialContainer(),
                    path=deque([]),
                    validator="contains",
                    schema_path=deque(["contains"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
