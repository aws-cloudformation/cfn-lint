"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbInstanceEngineVersion import DbInstanceEngineVersion


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceEngineVersion()
    yield rule


@pytest.fixture
def schema():
    return {
        "allOf": [
            {
                "if": {
                    "properties": {"Engine": {"type": "string"}},
                    "required": ["Engine"],
                },
                "then": {
                    "properties": {
                        "Engine": {
                            "enum": [
                                "mysql",
                            ]
                        }
                    }
                },
            },
            {
                "if": {
                    "properties": {
                        "Engine": {"const": "mysql"},
                        "EngineVersion": {"type": ["string", "number"]},
                    },
                    "required": ["Engine", "EngineVersion"],
                },
                "then": {
                    "properties": {
                        "EngineVersion": {
                            "enum": [
                                "8.0.39",
                                "8.0.40",
                                "8.0.41",
                                "8.4.3",
                                "8.4.4",
                            ]
                        }
                    }
                },
            },
        ],
    }


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Engine": "mysql",
            },
            [],
        ),
        (
            [],
            [],
        ),
        (
            {
                "Engine": "MySqL",  # API converts it appropriately
            },
            [],
        ),
        (
            {"Engine": {"Ref": "Engine"}},
            [],
        ),
        (
            {"Engine": {"Ref": "Engine"}, "EngineVeresion": {"Ref": "EngineVersion"}},
            [],
        ),
        (
            {
                "Engine": "MySqL",  # API converts it appropriately
                "EngineVeresion": {"Ref": "EngineVersion"},
            },
            [],
        ),
        (
            {"Engine": "foo"},
            [
                ValidationError(
                    "'foo' is not one of ['mysql']",
                    rule=DbInstanceEngineVersion(),
                    path=deque(["Engine"]),
                    validator="enum",
                    schema_path=deque(
                        ["allOf", 0, "then", "properties", "Engine", "enum"]
                    ),
                )
            ],
        ),
        (
            {"Engine": "mysql", "EngineVersion": "foo"},
            [
                ValidationError(
                    "'foo' is not one of ['8.0.39', '8.0.40', "
                    "'8.0.41', '8.4.3', '8.4.4']",
                    rule=DbInstanceEngineVersion(),
                    path=deque(["EngineVersion"]),
                    validator="enum",
                    schema_path=deque(
                        ["allOf", 1, "then", "properties", "EngineVersion", "enum"]
                    ),
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
    "instance,expected_paths",
    [
        ({"Engine": "mysql", "EngineVersion": "8.0"}, []),
        ({"Engine": "mysql", "EngineVersion": "8.4"}, []),
        ({"Engine": "mariadb", "EngineVersion": "10.11"}, []),
        ({"Engine": "mariadb", "EngineVersion": "11.4"}, []),
        ({"Engine": "postgres", "EngineVersion": "16"}, []),
        ({"Engine": "aurora-mysql", "EngineVersion": "8.0"}, []),
        ({"Engine": "mysql", "EngineVersion": "9.99"}, [deque(["EngineVersion"])]),
        ({"Engine": "mariadb", "EngineVersion": "9.99"}, [deque(["EngineVersion"])]),
    ],
)
def test_validate_shipped_schema(instance, expected_paths, validator):
    errs = list(DbInstanceEngineVersion().validate(validator, "", instance, {}))
    assert [err.path for err in errs] == expected_paths, f"Got {errs}"
    assert all(err.validator == "enum" for err in errs)
