"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceEngineVersionDeprecated import (
    DbInstanceEngineVersionDeprecated,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceEngineVersionDeprecated()
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
                        "deprecated and cannot be used to create new RDS DB instances"
                    ),
                    rule=DbInstanceEngineVersionDeprecated(),
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
                        "deprecated and cannot be used to create new RDS DB instances"
                    ),
                    rule=DbInstanceEngineVersionDeprecated(),
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


@pytest.mark.parametrize(
    "instance,expected_count",
    [
        # https://github.com/aws-cloudformation/cfn-lint/issues/4840
        # A shortened prefix is only deprecated when no available version
        # remains under it. RDS still resolves these to available releases.
        ({"Engine": "postgres", "EngineVersion": "16"}, 0),
        ({"Engine": "postgres", "EngineVersion": "17"}, 0),
        ({"Engine": "aurora-mysql", "EngineVersion": "8.0"}, 0),
        # Genuinely deprecated versions still warn.
        ({"Engine": "postgres", "EngineVersion": "16.1"}, 1),
        ({"Engine": "aurora-mysql", "EngineVersion": "5.7"}, 1),
    ],
)
def test_validate_shipped_schema(instance, expected_count, validator):
    errs = list(
        DbInstanceEngineVersionDeprecated().validate(validator, "", instance, {})
    )
    assert len(errs) == expected_count, f"Got {errs}"
    assert all("deprecated" in err.message for err in errs)
