"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceDbInstanceClassWithEngine import (
    DbInstanceDbInstanceClassWithEngine,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceDbInstanceClassWithEngine()
    yield rule


@pytest.fixture
def schema():
    return {
        "allOf": [
            {
                "if": {
                    "properties": {
                        "DBInstanceClass": {"type": "string"},
                        "Engine": {"const": "mysql", "type": "string"},
                        "EngineVersion": {
                            "pattern": "^(8\\.0\\..+|8\\.0)$",
                            "type": "string",
                        },
                    },
                    "required": ["Engine", "EngineVersion", "DBInstanceClass"],
                },
                "then": {
                    "properties": {
                        "DBInstanceClass": {
                            "enum": [
                                "db.t3.small",
                            ]
                        }
                    }
                },
            }
        ]
    }


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid because not an object",
            [],
            [],
        ),
        (
            "Valid class",
            {
                "Engine": "mysql",
                "EngineVersion": "8.0.39",
                "DBInstanceClass": "db.t3.small",
            },
            [],
        ),
        (
            "Valid because its missing EngineVersion",
            {
                "Engine": "mysql",
                "DBInstanceClass": "db.t2.small",
            },
            [],
        ),
        (
            "Valid because its missing Engine",
            {
                "EngineVersion": "8.0.39",
                "DBInstanceClass": "db.t2.small",
            },
            [],
        ),
        (
            "Invalid DBInstanceClass for Engine and EngineVersion",
            {
                "Engine": "mysql",
                "EngineVersion": "8.0.39",
                "DBInstanceClass": "db.t2.small",
            },
            [
                ValidationError(
                    "'db.t2.small' is not one of ['db.t3.small']",
                    validator="enum",
                    rule=DbInstanceDbInstanceClassWithEngine(),
                    path=deque(["DBInstanceClass"]),
                    schema_path=deque(
                        ["allOf", 0, "then", "properties", "DBInstanceClass", "enum"]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, schema, validator):
    rule._schema = schema
    errors = list(rule.validate(validator, "", instance, {}))

    assert errors == expected, f"Test {name!r} got {errors!r}"
