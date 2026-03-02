"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.guardduty.DetectorExclusiveProperties import (
    DetectorExclusiveProperties,
)


@pytest.fixture(scope="module")
def rule():
    rule = DetectorExclusiveProperties()
    yield rule


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        # Valid cases - should not trigger the rule
        (
            {
                "Enable": True,
                "Features": [
                    {"Name": "S3_DATA_EVENTS", "Status": "ENABLED"},
                    {"Name": "RUNTIME_MONITORING", "Status": "ENABLED"},
                ],
            },
            0,
            None,
        ),
        (
            {"Enable": True, "DataSources": {"S3Logs": {"Enable": True}}},
            0,
            None,
        ),
        (
            {
                "Enable": True,
            },  # Neither provided (schema validation handles missing properties)
            0,
            None,
        ),
        (
            [],
            0,
            None,
        ),
        # Invalid cases - should trigger the rule
        (
            {
                "Enable": True,
                "DataSources": {"S3Logs": {"Enable": True}},
                "Features": [
                    {"Name": "S3_DATA_EVENTS", "Status": "ENABLED"},
                    {"Name": "EBS_MALWARE_PROTECTION", "Status": "ENABLED"},
                ],
            },
            1,
            (
                "Both 'DataSources' and 'Features' were provided. "
                "You can provide only one; it is recommended to use 'Features'."
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
