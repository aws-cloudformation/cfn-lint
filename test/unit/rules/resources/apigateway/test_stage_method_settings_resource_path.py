"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.apigateway.StageMethodSettingsResourcePath import (
    StageMethodSettingsResourcePath,
)


@pytest.fixture(scope="module")
def rule():
    rule = StageMethodSettingsResourcePath()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "HttpMethod": "*",
                "ResourcePath": "api/{proxy+}",
                "LoggingLevel": "INFO",
            },
            [
                ValidationError(
                    "'api/{proxy+}' does not match '^/.*$'",
                    rule=StageMethodSettingsResourcePath(),
                    path=deque(["ResourcePath"]),
                    schema_path=deque(
                        ["then", "properties", "ResourcePath", "pattern"]
                    ),
                    validator="pattern",
                ),
            ],
        ),
        (
            {
                "HttpMethod": "*",
                "ResourcePath": "/*",
                "LoggingLevel": "INFO",
            },
            [],
        ),
        (
            {
                "HttpMethod": "*",
                "ResourcePath": "/",
                "MetricsEnabled": True,
            },
            [],
        ),
        (
            {
                "HttpMethod": "*",
                "ResourcePath": "api/{proxy+}",
            },
            [],
        ),
        (
            {
                "HttpMethod": "*",
                "ResourcePath": "no-slash",
                "ThrottlingBurstLimit": 100,
            },
            [
                ValidationError(
                    "'no-slash' does not match '^/.*$'",
                    rule=StageMethodSettingsResourcePath(),
                    path=deque(["ResourcePath"]),
                    schema_path=deque(
                        ["then", "properties", "ResourcePath", "pattern"]
                    ),
                    validator="pattern",
                ),
            ],
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
