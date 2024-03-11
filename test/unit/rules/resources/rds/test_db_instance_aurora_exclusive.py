"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.rds.DbInstanceAuroraExclusive import (
    DbInstanceAuroraExclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbInstanceAuroraExclusive()
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Engine": "aurora",
            },
            [],
        ),
        (
            {
                "Engine": "Auora",
            },
            [],
        ),
        (
            {
                "Engine": "aurora",
                "DeletionProtection": True,
            },
            [
                ValidationError(
                    (
                        "Additional properties are not allowed 'DeletionProtection' "
                        "when creating an Aurora instance"
                    ),
                    rule=DbInstanceAuroraExclusive(),
                    path=deque(["DeletionProtection"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "DeletionProtection"]),
                )
            ],
        ),
        (
            {
                "Engine": "Aurora",
                "DeletionProtection": True,
            },
            [
                ValidationError(
                    (
                        "Additional properties are not allowed 'DeletionProtection' "
                        "when creating an Aurora instance"
                    ),
                    rule=DbInstanceAuroraExclusive(),
                    path=deque(["DeletionProtection"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "DeletionProtection"]),
                )
            ],
        ),
        (
            {
                "Engine": "aurora",
                "DeletionProtection": True,
                "CopyTagsToSnapshot": True,
            },
            [
                ValidationError(
                    (
                        "Additional properties are not "
                        "allowed 'CopyTagsToSnapshot' "
                        "when creating an Aurora instance"
                    ),
                    rule=DbInstanceAuroraExclusive(),
                    path=deque(["CopyTagsToSnapshot"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "CopyTagsToSnapshot"]),
                ),
                ValidationError(
                    (
                        "Additional properties are not "
                        "allowed 'DeletionProtection' "
                        "when creating an Aurora instance"
                    ),
                    rule=DbInstanceAuroraExclusive(),
                    path=deque(["DeletionProtection"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "DeletionProtection"]),
                ),
            ],
        ),
        (
            [],
            [],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    for err in errs:
        print(err.validator)
        print(err.schema_path)
        print(err.path)
    assert errs == expected, f"Expected {expected} got {errs}"
