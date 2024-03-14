"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.rds.DbClusterServerlessExclusive import (
    DbClusterServerlessExclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterServerlessExclusive()
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "EngineMode": "serverless",
            },
            [],
        ),
        (
            {
                "EngineMode": "Serverless",
            },
            [],
        ),
        (
            {"EngineMode": "serverless", "ScalingConfiguration": "foo"},
            [
                ValidationError(
                    "Additional properties are not allowed ('ScalingConfiguration')",
                    rule=DbClusterServerlessExclusive(),
                    path=deque(["ScalingConfiguration"]),
                    validator=None,
                    schema_path=deque(["then", "properties", "ScalingConfiguration"]),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
