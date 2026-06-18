"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.apigateway.StageMethodSettingsIgnored import (
    StageMethodSettingsIgnored,
)


@pytest.fixture(scope="module")
def rule():
    rule = StageMethodSettingsIgnored()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"HttpMethod": "*", "ResourcePath": "api/{proxy+}"},
            [
                ValidationError(
                    "MethodSettings entry has no effect without a setting "
                    "property (LoggingLevel, MetricsEnabled, CachingEnabled, etc.)",
                ),
            ],
        ),
        (
            {"HttpMethod": "*", "ResourcePath": "/*", "LoggingLevel": "INFO"},
            [],
        ),
        (
            {"HttpMethod": "*", "ResourcePath": "/*", "MetricsEnabled": True},
            [],
        ),
        (
            {"HttpMethod": "*", "ResourcePath": "/*", "CachingEnabled": True},
            [],
        ),
        (
            {},
            [],
        ),
        (
            "not a dict",
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
