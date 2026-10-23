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
        # Every ignored property gets its own warning: the rule runs with
        # all_matches=True and applies the per-property message to each
        # error, so setting three must yield three warnings.
        (
            {
                "SourceDBInstanceIdentifier": "foo",
                "StorageEncrypted": False,
                "MasterUsername": "foo",
                "DBName": "foo",
            },
            [
                ValidationError(
                    "'DBName' is ignored on a read replica and "
                    "inherited from the source DB instance",
                    rule=DbInstanceSourceDBInstanceIdentifier(),
                    path=deque(["DBName"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "DBName"]),
                ),
                ValidationError(
                    "'MasterUsername' is ignored on a read replica and "
                    "inherited from the source DB instance",
                    rule=DbInstanceSourceDBInstanceIdentifier(),
                    path=deque(["MasterUsername"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "MasterUsername"]),
                ),
                ValidationError(
                    "'StorageEncrypted' is ignored on a read replica and "
                    "inherited from the source DB instance",
                    rule=DbInstanceSourceDBInstanceIdentifier(),
                    path=deque(["StorageEncrypted"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "StorageEncrypted"]),
                ),
            ],
        ),
        # Presence of SourceDBInstanceIdentifier is what makes it a read
        # replica, not a resolvable string value: a Ref to a source in the
        # same template must still warn.
        (
            {
                "SourceDBInstanceIdentifier": {"Ref": "Src"},
                "StorageEncrypted": False,
            },
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
