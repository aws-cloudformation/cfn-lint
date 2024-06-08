"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbClusterMultiAz import DbClusterMultiAz


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterMultiAz()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Engine": "mysql",
                "AllocatedStorage": 100,
                "DBClusterInstanceClass": "foo",
                "Iops": 100,
                "StorageType": "io1",
            },
            [],
        ),
        (
            {
                "Engine": "aurora-mysql",
                "AllocatedStorage": 100,
                "DBClusterInstanceClass": "foo",
                "Iops": 100,
            },
            [],
        ),
        (
            {
                "Engine": {"Ref": "Engine"},
                "AllocatedStorage": 100,
                "DBClusterInstanceClass": "foo",
                "Iops": 100,
            },
            [],
        ),
        (
            {
                "Engine": "mysql",
                "AllocatedStorage": 100,
                "DBClusterInstanceClass": "foo",
                "Iops": 100,
                "StorageType": "aurora",
            },
            [
                ValidationError(
                    ("'aurora' is not one of ['io1', 'io2', 'gp3']"),
                    rule=DbClusterMultiAz(),
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
                "Engine": "mysql",
            },
            [
                ValidationError(
                    ("'AllocatedStorage' is a required property"),
                    rule=DbClusterMultiAz(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                ),
                ValidationError(
                    ("'DBClusterInstanceClass' is a required property"),
                    rule=DbClusterMultiAz(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                ),
                ValidationError(
                    ("'Iops' is a required property"),
                    rule=DbClusterMultiAz(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                ),
                ValidationError(
                    ("'StorageType' is a required property"),
                    rule=DbClusterMultiAz(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                ),
            ],
        ),
        (
            {
                "Engine": "mysql",
                "Domain": "Foo",
                "AllocatedStorage": 100,
                "DBClusterInstanceClass": "foo",
                "Iops": 100,
                "StorageType": "io1",
            },
            [
                ValidationError(
                    (
                        "Additional properties are not allowed 'Domain' "
                        "when creating Multi-AZ cluster"
                    ),
                    rule=DbClusterMultiAz(),
                    path=deque(["Domain"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "Domain"]),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
