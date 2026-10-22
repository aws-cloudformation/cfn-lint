"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceSourceDBInstanceIdentifier import (
    DbInstanceSourceDBInstanceIdentifier,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceSourceDBInstanceIdentifier()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "SourceDBInstanceIdentifier": "foo",
            },
            [],
        ),
        (
            {},
            [],
        ),
        (
            {"SourceDBInstanceIdentifier": "foo", "StorageEncrypted": True},
            [
                ValidationError(
                    "'StorageEncrypted' is ignored on a read replica and "
                    "inherited from the source DB instance",
                    rule=DbInstanceSourceDBInstanceIdentifier(),
                    path=deque(["StorageEncrypted"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "StorageEncrypted"]),
                )
            ],
        ),
        (
            {"SourceDBInstanceIdentifier": "foo", "MasterUsername": "foo"},
            [
                ValidationError(
                    "'MasterUsername' is ignored on a read replica and "
                    "inherited from the source DB instance",
                    rule=DbInstanceSourceDBInstanceIdentifier(),
                    path=deque(["MasterUsername"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "MasterUsername"]),
                )
            ],
        ),
        (
            {"SourceDBInstanceIdentifier": "foo", "DBName": "foo"},
            [
                ValidationError(
                    "'DBName' is ignored on a read replica and "
                    "inherited from the source DB instance",
                    rule=DbInstanceSourceDBInstanceIdentifier(),
                    path=deque(["DBName"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "DBName"]),
                )
            ],
        ),
        # BackupRetentionPeriod and PreferredBackupWindow are honored on
        # read replicas (live verified), so they must not warn.
        (
            {"SourceDBInstanceIdentifier": "foo", "BackupRetentionPeriod": 7},
            [],
        ),
        (
            {
                "SourceDBInstanceIdentifier": "foo",
                "PreferredBackupWindow": "06:00-07:00",
            },
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
