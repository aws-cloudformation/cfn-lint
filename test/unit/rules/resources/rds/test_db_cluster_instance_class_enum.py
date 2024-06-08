"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbClusterInstanceClassEnum import (
    DbClusterInstanceClassEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterInstanceClassEnum()
    rule._schema = {
        "us-east-1": {
            "allOf": [
                {
                    "if": {
                        "properties": {
                            "DBClusterInstanceClass": {"type": "string"},
                            "Engine": {"const": "mysql"},
                        },
                        "required": ["Engine", "DBClusterInstanceClass"],
                    },
                    "then": {
                        "properties": {
                            "DBClusterInstanceClass": {
                                "enum": [
                                    "db.m5d.12xlarge",
                                    "db.m5d.16xlarge",
                                ]
                            }
                        }
                    },
                }
            ]
        }
    }
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Engine": "mysql", "DBClusterInstanceClass": "db.m5d.12xlarge"},
            [],
        ),
        (
            {"Engine": "aurora-mysql", "DBClusterInstanceClass": "a"},
            [],
        ),
        (
            {
                "Engine": {"Ref": "Engine"},
                "DBClusterInstanceClass": {"Ref": "DBInstanceClass"},
            },
            [],
        ),
        (
            {
                "Engine": "mysql",
                "DBClusterInstanceClass": {"Ref": "DBInstanceClass"},
            },
            [],
        ),
        (
            {
                "Engine": "mysql",
                "DBClusterInstanceClass": "a",
            },
            [
                ValidationError(
                    (
                        "'a' is not one of ['db.m5d.12xlarge', "
                        "'db.m5d.16xlarge'] in 'us-east-1'"
                    ),
                    rule=DbClusterInstanceClassEnum(),
                    path=deque(["DBClusterInstanceClass"]),
                    validator="enum",
                    schema_path=deque(
                        [
                            "allOf",
                            0,
                            "then",
                            "properties",
                            "DBClusterInstanceClass",
                            "enum",
                        ]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
