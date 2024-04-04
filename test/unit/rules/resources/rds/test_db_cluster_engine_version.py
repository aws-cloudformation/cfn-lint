"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.rds.DbClusterEngineVersion import DbClusterEngineVersion


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterEngineVersion()
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
                "Engine": "mysql",
                "EngineVersion": "5.7.37",
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
                "Engine": "mysql",
                "EngineVersion": {"Ref": "EngineVersion"},
            },
            [],
        ),
        (
            {"Engine": "foo"},
            [
                ValidationError(
                    (
                        "'foo' is not one of ['aurora-mysql', 'aurora-postgresql', "
                        "'mysql', 'postgres']"
                    ),
                    rule=DbClusterEngineVersion(),
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
                    rule=DbClusterEngineVersion(),
                    path=deque(["EngineVersion"]),
                    validator="enum",
                    schema_path=deque(
                        ["allOf", 3, "then", "properties", "EngineVersion", "enum"]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
