"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbClusterEngineVersionDeprecated import (
    DbClusterEngineVersionDeprecated,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterEngineVersionDeprecated()
    yield rule


@pytest.fixture
def schema():
    return {
        "allOf": [
            {
                "if": {
                    "properties": {
                        "Engine": {"const": "postgres"},
                        "EngineVersion": {
                            "type": ["string", "number"],
                            "enum": ["16.1", "16.2"],
                        },
                    },
                    "required": ["Engine", "EngineVersion"],
                },
                "then": False,
            },
        ],
    }


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Engine": "postgres",
                "EngineVersion": "16.11",
            },
            [],
        ),
        (
            {
                "Engine": {"Ref": "Engine"},
                "EngineVersion": {"Ref": "EngineVersion"},
            },
            [],
        ),
        (
            {
                "Engine": "postgres",
                "EngineVersion": {"Ref": "EngineVersion"},
            },
            [],
        ),
        (
            {"Engine": "postgres", "EngineVersion": "16.1"},
            [
                ValidationError(
                    (
                        "Engine version '16.1' for engine 'postgres' is "
                        "deprecated and cannot be used to create new RDS DB clusters"
                    ),
                    rule=DbClusterEngineVersionDeprecated(),
                    path=deque([]),
                    schema_path=deque(["allOf", 0, "then"]),
                    validator=None,
                )
            ],
        ),
        (
            {"Engine": "postgres", "EngineVersion": "16.2"},
            [
                ValidationError(
                    (
                        "Engine version '16.2' for engine 'postgres' is "
                        "deprecated and cannot be used to create new RDS DB clusters"
                    ),
                    rule=DbClusterEngineVersionDeprecated(),
                    path=deque([]),
                    schema_path=deque(["allOf", 0, "then"]),
                    validator=None,
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator, schema):
    rule._schema = schema
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
