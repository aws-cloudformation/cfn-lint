"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbClusterSourceDBClusterIdentifier import (
    DbClusterSourceDBClusterIdentifier,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterSourceDBClusterIdentifier()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "SourceDBClusterIdentifier": "foo",
            },
            [],
        ),
        (
            {},
            [],
        ),
        (
            {"SourceDBClusterIdentifier": "foo", "MasterUsername": "foo"},
            [
                ValidationError(
                    (
                        "Additional properties are ignored ('MasterUsername', "
                        "'MasterUserPassword', 'StorageEncrypted')"
                    ),
                    rule=DbClusterSourceDBClusterIdentifier(),
                    path=deque(["MasterUsername"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "MasterUsername"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
