"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.backup.BackupPlanLifecycleRule import (
    BackupPlanLifecycleRule,
)


@pytest.fixture(scope="module")
def rule():
    rule = BackupPlanLifecycleRule()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {},
            [],
        ),
        (
            {
                "DeleteAfterDays": 100,
                "MoveToColdStorageAfterDays": 10,
            },
            [],
        ),
        (
            {
                "DeleteAfterDays": "foo",
                "MoveToColdStorageAfterDays": 10,
            },
            [],
        ),
        (
            {
                "DeleteAfterDays": 100,
                "MoveToColdStorageAfterDays": "foo",
            },
            [],
        ),
        (
            {
                "DeleteAfterDays": 10,
                "MoveToColdStorageAfterDays": 30,
            },
            [
                ValidationError(
                    (
                        "DeleteAfterDays 10 must be at least 90 "
                        "days after MoveToColdStorageAfterDays 30"
                    ),
                    rule=BackupPlanLifecycleRule(),
                    path=deque(["DeleteAfterDays"]),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
