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


# Scenarios validated against CloudFormation/ECS on 2026-06-03:
# - 1 container, no Essential: succeeds (defaults to true)
# - 2 containers, no Essential: succeeds (both default to true)
# - 1 Essential:false + 1 no Essential: succeeds (second defaults to true)
# - All containers Essential:false: fails ("doesn't have any essential container")
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
            [{"Name": "container"}],  # validated
            [],
        ),
        (
            [{"Name": "container-one"}, {"Name": "container-two"}],  # validated
            [],
        ),
        (
            [{"Essential": False}, {"Name": "main"}],  # validated
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
            [{"Essential": False}, {"Essential": False}],
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
                    validator="minItems",
                    schema_path=deque(["minItems"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
