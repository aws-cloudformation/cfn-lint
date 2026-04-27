"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceReplicaMode import DbInstanceReplicaMode


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceReplicaMode()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Engine": "oracle-ee", "ReplicaMode": "open-read-only"},
            [],
        ),
        (
            {"Engine": "oracle-ee", "ReplicaMode": "mounted"},
            [],
        ),
        (
            {"Engine": "db2-ae", "ReplicaMode": "open-read-only"},
            [],
        ),
        (
            {"Engine": "oracle-ee"},
            [],
        ),
        (
            {"Engine": "postgres", "ReplicaMode": "invalid"},
            [],
        ),
        (
            {"Engine": "oracle-ee", "ReplicaMode": "invalid"},
            [
                ValidationError(
                    "'invalid' is not one of ['mounted', 'open-read-only']",
                    rule=DbInstanceReplicaMode(),
                    path=deque(["ReplicaMode"]),
                    schema_path=deque(["then", "properties", "ReplicaMode", "enum"]),
                    validator="enum",
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
