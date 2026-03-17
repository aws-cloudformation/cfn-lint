"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.rds.DbInstanceClusterEngine import DbInstanceClusterEngine


@pytest.fixture(scope="module")
def rule():
    return DbInstanceClusterEngine()


_template = {
    "Resources": {
        "Cluster": {
            "Type": "AWS::RDS::DBCluster",
            "Properties": {
                "Engine": "aurora-mysql",
                "MasterUsername": "admin",
                "MasterUserPassword": "password",
            },
        },
        "Instance": {
            "Type": "AWS::RDS::DBInstance",
            "Properties": {
                "DBClusterIdentifier": {"Ref": "Cluster"},
                "DBInstanceClass": "db.r5.large",
                "Engine": "aurora-mysql",
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # Matching engines — valid
        (
            _template,
            deque(["Resources", "Instance", "Properties"]),
            [],
        ),
        # Mismatched engines — invalid
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Instance": {
                        "Type": "AWS::RDS::DBInstance",
                        "Properties": {
                            "DBClusterIdentifier": {"Ref": "Cluster"},
                            "DBInstanceClass": "db.r5.large",
                            "Engine": "aurora-postgresql",
                        },
                    },
                },
            },
            deque(["Resources", "Instance", "Properties"]),
            [
                ValidationError(
                    "'aurora-mysql' was expected",
                    validator="const",
                    rule=DbInstanceClusterEngine(),
                    path=deque(["Engine"]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "properties",
                            "local",
                            "properties",
                            "Engine",
                            "const",
                        ]
                    ),
                ),
            ],
        ),
        # No DBClusterIdentifier — valid (standalone instance)
        (
            {
                "Resources": {
                    **_template["Resources"],
                    "Instance": {
                        "Type": "AWS::RDS::DBInstance",
                        "Properties": {
                            "DBInstanceClass": "db.r5.large",
                            "Engine": "mysql",
                        },
                    },
                },
            },
            deque(["Resources", "Instance", "Properties"]),
            [],
        ),
    ],
    indirect=["template"],
)
def test_validate(template, start_path, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"Expected {expected} got {errs}"
