"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceAuroraExclusive import (
    DbInstanceAuroraExclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceAuroraExclusive()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Engine": "aurora",
            },
            [],
        ),
        (
            {
                "Engine": "Auora",
            },
            [],
        ),
        (
            {"MasterUserPassword": "Test"},
            [],
        ),
        (
            {
                "Engine": "aurora",
                "DeletionProtection": True,
            },
            [
                ValidationError(
                    "Additional properties are not allowed (['DeletionProtection'])",
                    rule=DbInstanceAuroraExclusive(),
                    path=deque([]),
                    instance={"Engine": "aurora", "DeletionProtection": True},
                    validator="not",
                    schema_path=deque(["then", "not"]),
                )
            ],
        ),
        (
            {
                "Engine": "Aurora",
                "DeletionProtection": True,
            },
            [
                ValidationError(
                    "Additional properties are not allowed (['DeletionProtection'])",
                    rule=DbInstanceAuroraExclusive(),
                    path=deque([]),
                    instance={"Engine": "aurora", "DeletionProtection": True},
                    validator="not",
                    schema_path=deque(["then", "not"]),
                )
            ],
        ),
        (
            {
                "Engine": "aurora",
                "DeletionProtection": True,
                "CopyTagsToSnapshot": True,
            },
            [
                ValidationError(
                    (
                        "Additional properties are not "
                        "allowed (['DeletionProtection', "
                        "'CopyTagsToSnapshot'])"
                    ),
                    rule=DbInstanceAuroraExclusive(),
                    path=deque([]),
                    instance={
                        "Engine": "aurora",
                        "DeletionProtection": True,
                        "CopyTagsToSnapshot": True,
                    },
                    validator="not",
                    schema_path=deque(["then", "not"]),
                )
            ],
        ),
        (
            [],
            [],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
