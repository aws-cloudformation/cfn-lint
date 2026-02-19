"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.lmbd.FunctionLogLevelLogFormat import (
    FunctionLogLevelLogFormat,
)


@pytest.fixture(scope="module")
def rule():
    rule = FunctionLogLevelLogFormat()
    yield rule


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        (
            {
                "LoggingConfig": {
                    "LogFormat": "JSON",
                    "SystemLogLevel": "INFO",
                }
            },
            0,
            None,
        ),
        (
            {
                "LoggingConfig": {
                    "LogFormat": "Text",
                }
            },
            0,
            None,
        ),
        (
            [],  # wrong type
            0,
            None,
        ),
        (
            {
                "LoggingConfig": {
                    "LogFormat": "Text",
                    "SystemLogLevel": "INFO",
                }
            },
            1,
            (
                "LogLevel is not supported when LogFormat is set to 'Text'. "
                "Remove LogLevel from your request or change the LogFormat to 'JSON'"
            ),
        ),
    ],
)
def test_validate(instance, expected_count, expected_message, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, (
        f"Expected {expected_count} errors got {len(errs)}"
    )
    if expected_message:
        assert errs[0].message == expected_message
