"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceReplicaModeIgnored import (
    DbInstanceReplicaModeIgnored,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceReplicaModeIgnored()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Engine": "oracle-ee", "ReplicaMode": "open-read-only"},
            [],
        ),
        (
            {"Engine": "db2-ae", "ReplicaMode": "mounted"},
            [],
        ),
        (
            {"Engine": "custom-oracle-ee", "ReplicaMode": "mounted"},
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
            "not a dict",
            [],
        ),
        (
            {"ReplicaMode": "mounted"},
            [],
        ),
        (
            {"Engine": ["postgres"], "ReplicaMode": "mounted"},
            [],
        ),
        (
            {"Engine": "postgres", "ReplicaMode": "open-read-only"},
            [
                ValidationError(
                    "'ReplicaMode' is ignored when 'Engine' is 'postgres'",
                    path=deque(["ReplicaMode"]),
                ),
            ],
        ),
        (
            {"Engine": "aurora-postgresql", "ReplicaMode": "mounted"},
            [
                ValidationError(
                    "'ReplicaMode' is ignored when 'Engine' is 'aurora-postgresql'",
                    path=deque(["ReplicaMode"]),
                ),
            ],
        ),
        (
            {"Engine": "mysql", "ReplicaMode": "open-read-only"},
            [
                ValidationError(
                    "'ReplicaMode' is ignored when 'Engine' is 'mysql'",
                    path=deque(["ReplicaMode"]),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
