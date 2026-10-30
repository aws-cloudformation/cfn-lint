"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from collections import deque

import pytest

from cfnlint.api import lint
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
                "Engine": "postgres",
                "AllocatedStorage": 100,
                "DBClusterInstanceClass": "foo",
                "Iops": 1000,
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
                    "'aurora' is not one of ['io1', 'io2', 'gp3']",
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
                    "'AllocatedStorage' is a required property",
                    rule=DbClusterMultiAz(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "else", "required"]),
                ),
                ValidationError(
                    "'DBClusterInstanceClass' is a required property",
                    rule=DbClusterMultiAz(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                ),
                ValidationError(
                    "'Iops' is a required property",
                    rule=DbClusterMultiAz(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                ),
            ],
        ),
        (
            {
                "Engine": "postgres",
                "DBClusterInstanceClass": "foo",
                "Iops": 1000,
                "StorageType": "io1",
                "ReplicationSourceIdentifier": {
                    "Fn::GetAtt": ["SourceInstance", "DBInstanceArn"]
                },
            },
            [],
        ),
        (
            {
                "Engine": "postgres",
                "DBClusterInstanceClass": "foo",
                "Iops": 1000,
                "ReplicationSourceIdentifier": {"Ref": "SourceDbArn"},
            },
            [],
        ),
        (
            {
                "Engine": "postgres",
                "DBClusterInstanceClass": "foo",
                "Iops": 1000,
                "StorageType": "gp2",
                "ReplicationSourceIdentifier": {"Ref": "SourceDbArn"},
            },
            [
                ValidationError(
                    "'gp2' is not one of ['io1', 'io2', 'gp3']",
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
                "AllocatedStorage": 100,
                "DBClusterInstanceClass": "foo",
                "Iops": 1000,
                "StorageType": "io1",
                "ReplicationSourceIdentifier": {"Ref": "SourceDbArn"},
            },
            [
                ValidationError(
                    "'AllocatedStorage' is not allowed on a Multi-AZ DB "
                    "cluster read replica (ReplicationSourceIdentifier is set)",
                    rule=DbClusterMultiAz(),
                    path=deque(["AllocatedStorage"]),
                    validator=None,
                    schema_path=deque(
                        ["then", "then", "properties", "AllocatedStorage"]
                    ),
                ),
            ],
        ),
        (
            {
                "Engine": "mysql",
                "ReplicationSourceIdentifier": {"Ref": "SourceDbArn"},
            },
            [
                ValidationError(
                    "'DBClusterInstanceClass' is a required property",
                    rule=DbClusterMultiAz(),
                    path=deque([]),
                    validator="required",
                    schema_path=deque(["then", "required"]),
                ),
                ValidationError(
                    "'Iops' is a required property",
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
                    "Additional properties are not allowed 'Domain' "
                    "when creating Multi-AZ cluster",
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


@pytest.mark.parametrize(
    "name,allocated_storage,expected",
    [
        (
            "AllocatedStorage only on the primary branch",
            {"Fn::If": ["IsReplica", {"Ref": "AWS::NoValue"}, 100]},
            [],
        ),
        (
            "AllocatedStorage on both branches",
            100,
            [
                "'AllocatedStorage' is not allowed on a Multi-AZ DB "
                "cluster read replica (ReplicationSourceIdentifier is set)"
            ],
        ),
    ],
)
def test_conditional_read_replica(name, allocated_storage, expected):
    template = {
        "Parameters": {"SourceDbArn": {"Type": "String", "Default": ""}},
        "Conditions": {
            "IsReplica": {"Fn::Not": [{"Fn::Equals": [{"Ref": "SourceDbArn"}, ""]}]}
        },
        "Resources": {
            "Cluster": {
                "Type": "AWS::RDS::DBCluster",
                "Properties": {
                    "Engine": "postgres",
                    "DBClusterInstanceClass": "db.m6gd.large",
                    "Iops": 1000,
                    "StorageType": "io1",
                    "AllocatedStorage": allocated_storage,
                    "ReplicationSourceIdentifier": {
                        "Fn::If": [
                            "IsReplica",
                            {"Ref": "SourceDbArn"},
                            {"Ref": "AWS::NoValue"},
                        ]
                    },
                },
            }
        },
    }
    matches = lint(json.dumps(template), regions=["us-east-1"])

    assert [
        match.message for match in matches if match.rule.id == "E3692"
    ] == expected, f"Test {name!r} failed with {matches!r}"
