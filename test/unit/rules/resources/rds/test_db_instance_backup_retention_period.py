"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceBackupRetentionPeriod import (
    DbInstanceBackupRetentionPeriod,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceBackupRetentionPeriod()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Engine": "postgres", "BackupRetentionPeriod": 7},
            [],
        ),
        (
            {"Engine": "postgres", "BackupRetentionPeriod": 35},
            [],
        ),
        (
            {"Engine": "aurora-mysql", "BackupRetentionPeriod": 36},
            [],
        ),
        (
            {"Engine": "postgres", "SourceDBInstanceIdentifier": "source-db"},
            [],
        ),
        (
            {"Engine": "postgres"},
            [],
        ),
        (
            {},
            [],
        ),
        (
            {"Engine": "postgres", "BackupRetentionPeriod": 36},
            [
                ValidationError(
                    (
                        "BackupRetentionPeriod 36 exceeds maximum of 35"
                        " for non-Aurora standalone instances"
                    ),
                    rule=DbInstanceBackupRetentionPeriod(),
                    path=deque(["BackupRetentionPeriod"]),
                    validator="maximum",
                    schema_path=deque(
                        ["then", "properties", "BackupRetentionPeriod", "maximum"]
                    ),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
