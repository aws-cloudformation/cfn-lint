"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbClusterServerlessExclusive import (
    DbClusterServerlessExclusive,
)


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterServerlessExclusive()
    yield rule


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
            {"EngineMode": "serverless", "ServerlessV2ScalingConfiguration": "foo"},
            [
                ValidationError(
                    (
                        "EngineMode 'serverless'  doesn't allow additional "
                        "properties 'ServerlessV2ScalingConfiguration'"
                    ),
                    rule=DbClusterServerlessExclusive(),
                    path=deque(["ServerlessV2ScalingConfiguration"]),
                    validator=None,
                    schema_path=deque(
                        [
                            "allOf",
                            1,
                            "then",
                            "properties",
                            "ServerlessV2ScalingConfiguration",
                        ]
                    ),
                )
            ],
        ),
        (
            {"EngineMode": "provisioned", "ScalingConfiguration": "foo"},
            [
                ValidationError(
                    (
                        "EngineMode 'provisioned'  doesn't allow "
                        "additional properties 'ScalingConfiguration'"
                    ),
                    rule=DbClusterServerlessExclusive(),
                    path=deque(["ScalingConfiguration"]),
                    validator=None,
                    schema_path=deque(
                        ["allOf", 0, "then", "properties", "ScalingConfiguration"]
                    ),
                )
            ],
        ),
        (
            {"ServerlessV2ScalingConfiguration": "foo"},
            [],
        ),
        (
            {"ScalingConfiguration": "foo"},
            [
                ValidationError(
                    (
                        "Additional properties are not allowed "
                        "('ScalingConfiguration')"
                    ),
                    rule=DbClusterServerlessExclusive(),
                    path=deque(["ScalingConfiguration"]),
                    validator=None,
                    schema_path=deque(
                        ["allOf", 2, "then", "properties", "ScalingConfiguration"]
                    ),
                )
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
