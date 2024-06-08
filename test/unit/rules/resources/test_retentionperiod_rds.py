"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.RetentionPeriodOnResourceTypesWithAutoExpiringContent import (  # noqa: E501
    RetentionPeriodOnResourceTypesWithAutoExpiringContent,
)


@pytest.fixture(scope="module")
def rule():
    rule = RetentionPeriodOnResourceTypesWithAutoExpiringContent()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyRdsDbInstance": {
                "Type": "AWS::RDS::DBInstance",
            }
        }
    }


@pytest.fixture
def path():
    return Path(
        path=deque(["Resources", "MyRdsDbInstance", "Properties"]),
        cfn_path=deque(["Resources", "AWS::RDS::DBInstance", "Properties"]),
    )


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid retention period",
            {"MessageRetentionPeriod": "90"},
            [],
        ),
        (
            "Valid with SourceDBInstanceIdentifier",
            {"SourceDBInstanceIdentifier": "source-db"},
            [],
        ),
        (
            "Invalid when not specified",
            {
                "Engine": "mysql",
            },
            [
                ValidationError(
                    (
                        "'BackupRetentionPeriod' is a required property (The "
                        "default retention period will delete the data after "
                        "a pre-defined time. Set an explicit values to avoid "
                        "data loss on resource)"
                    ),
                    rule=RetentionPeriodOnResourceTypesWithAutoExpiringContent(),
                    schema_path=deque(["then", "required"]),
                    validator="required",
                    validator_value=["BackupRetentionPeriod"],
                )
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, False, instance, {}))

    assert errs == expected, f"Test {name!r} got {errs!r}"
