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
            {"Engine": "aurora-mysql", "DBClusterIdentifier": "my-cluster"},
            [],
        ),
        (
            {"Engine": "postgres", "BackupRetentionPeriod": 36},
            [
                ValidationError(
                    "36 is greater than the maximum of 35",
                    rule=DbInstanceBackupRetentionPeriod(),
                    path=deque(["BackupRetentionPeriod"]),
                    schema_path=deque(
                        [
                            "allOf",
                            1,
                            "then",
                            "properties",
                            "BackupRetentionPeriod",
                            "maximum",
                        ]
                    ),
                    validator="maximum",
                    schema={"maximum": 35},
                    instance=36,
                ),
            ],
        ),
        (
            {
                "Engine": "aurora-mysql",
                "DBClusterIdentifier": "my-cluster",
                "BackupRetentionPeriod": 14,
            },
            [
                ValidationError(
                    (
                        "'BackupRetentionPeriod' is not allowed when "
                        "'DBClusterIdentifier' is specified. Set backup "
                        "retention period on the DB cluster instead."
                    ),
                    rule=DbInstanceBackupRetentionPeriod(),
                    path=deque(["BackupRetentionPeriod"]),
                    schema_path=deque(
                        [
                            "allOf",
                            0,
                            "then",
                            "properties",
                            "BackupRetentionPeriod",
                        ]
                    ),
                    validator=None,
                    schema=False,
                    instance=14,
                ),
            ],
        ),
        (
            {
                "Engine": "mysql",
                "DBClusterIdentifier": "my-maz-cluster",
                "BackupRetentionPeriod": 7,
            },
            [
                ValidationError(
                    (
                        "'BackupRetentionPeriod' is not allowed when "
                        "'DBClusterIdentifier' is specified. Set backup "
                        "retention period on the DB cluster instead."
                    ),
                    rule=DbInstanceBackupRetentionPeriod(),
                    path=deque(["BackupRetentionPeriod"]),
                    schema_path=deque(
                        [
                            "allOf",
                            0,
                            "then",
                            "properties",
                            "BackupRetentionPeriod",
                        ]
                    ),
                    validator=None,
                    schema=False,
                    instance=7,
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
