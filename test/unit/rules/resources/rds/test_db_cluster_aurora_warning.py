"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.rds.DbClusterAuroraWarning import DbClusterAuroraWarning


@pytest.fixture(scope="module")
def rule():
    rule = DbClusterAuroraWarning()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Engine": "aurora-mysql", "EngineMode": "serverless"},
            [],
        ),
        (
            {
                "Engine": "aurora-mysql",
                "EngineMode": "provisioned",
                "PerformanceInsightsEnabled": True,
            },
            [],
        ),
        (
            {
                "Engine": "aurora-mysql",
                "PerformanceInsightsEnabled": True,
            },
            [],
        ),
        (
            {
                "Engine": "aurora-mysql",
                "EngineMode": "serverless",
                "PerformanceInsightsEnabled": True,
            },
            [
                ValidationError(
                    (
                        "Additional properties are not allowed "
                        "'PerformanceInsightsEnabled' when creating Aurora cluster"
                    ),
                    rule=DbClusterAuroraWarning(),
                    path=deque(["PerformanceInsightsEnabled"]),
                    validator=None,
                    schema_path=deque(
                        ["then", "properties", "PerformanceInsightsEnabled"]
                    ),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
