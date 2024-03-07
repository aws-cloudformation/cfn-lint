"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.rds.DbInstanceEngineVersion import DbInstanceEngineVersion


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceEngineVersion()
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


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
            {
                "Engine": "MySqL",  # API converts it appropriately
            },
            [],
        ),
        (
            {"Engine": "foo"},
            [
                ValidationError(
                    (
                        "'foo' is not one of ['aurora-mysql', 'aurora-postgresql', "
                        "'custom-oracle-ee', 'custom-oracle-ee-cdb', "
                        "'custom-sqlserver-ee', 'custom-sqlserver-se', "
                        "'custom-sqlserver-web', 'db2-ae', 'db2-se', 'mariadb', "
                        "'mysql', 'oracle-ee', 'oracle-ee-cdb', 'oracle-se2', "
                        "'oracle-se2-cdb', 'postgres', 'sqlserver-ee', "
                        "'sqlserver-se', 'sqlserver-ex', 'sqlserver-web']"
                    ),
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
                    (
                        "'foo' is not one of ['5.7.37', '5.7.38', '5.7.39', '5.7.40', "
                        "'5.7.41', '5.7.42', '5.7.43', '5.7.44', '8.0.28', '8.0.31', "
                        "'8.0.32', '8.0.33', '8.0.34', '8.0.35', '8.0.36']"
                    ),
                    rule=DbInstanceEngineVersion(),
                    path=deque(["EngineVersion"]),
                    validator="enum",
                    schema_path=deque(
                        ["allOf", 9, "then", "properties", "EngineVersion", "enum"]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    for err in errs:
        print(err.schema_path)
    assert errs == expected, f"Expected {expected} got {errs}"
