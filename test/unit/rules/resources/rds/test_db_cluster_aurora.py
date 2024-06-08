"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbClusterAurora import DbClusterAurora


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterAurora()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Engine": "aurora-mysql",
            },
            [],
        ),
        (
            {"Engine": "aurora-mysql", "StorageType": "aurora"},
            [],
        ),
        (
            {"Engine": "aurora-mysql", "StorageType": "io1"},
            [
                ValidationError(
                    ("'io1' is not one of ['aurora', 'aurora-iopt1']"),
                    rule=DbClusterAurora(),
                    path=deque(["StorageType"]),
                    validator="enum",
                    schema_path=deque(
                        ["then", "properties", "StorageType", "then", "enum"]
                    ),
                ),
            ],
        ),
        (
            {
                "Engine": "aurora-mysql",
                "AllocatedStorage": 100,
                "DBClusterInstanceClass": "foo",
                "Iops": 100,
            },
            [
                ValidationError(
                    (
                        "Additional properties are not allowed "
                        "'AllocatedStorage' when creating Aurora cluster"
                    ),
                    rule=DbClusterAurora(),
                    path=deque(["AllocatedStorage"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "AllocatedStorage"]),
                ),
                ValidationError(
                    (
                        "Additional properties are not allowed "
                        "'DBClusterInstanceClass' when creating Aurora cluster"
                    ),
                    rule=DbClusterAurora(),
                    path=deque(["DBClusterInstanceClass"]),
                    schema_path=deque(["then", "properties", "DBClusterInstanceClass"]),
                    validator=None,
                ),
                ValidationError(
                    (
                        "Additional properties are not allowed 'Iops' "
                        "when creating Aurora cluster"
                    ),
                    rule=DbClusterAurora(),
                    path=deque(["Iops"]),
                    schema_path=deque(["then", "properties", "Iops"]),
                    validator=None,
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
