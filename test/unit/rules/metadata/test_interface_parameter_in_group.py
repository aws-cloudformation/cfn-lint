"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.metadata.InterfaceParameterInGroup import InterfaceParameterInGroup


@pytest.fixture(scope="module")
def rule():
    return InterfaceParameterInGroup()


@pytest.fixture
def template():
    return {
        "Parameters": {
            "VpcId": {"Type": "String"},
            "SubnetId": {"Type": "String"},
        },
    }


@pytest.mark.parametrize(
    "name,instance,expected_count",
    [
        (
            "All parameters listed in ParameterGroups",
            {
                "ParameterGroups": [
                    {
                        "Label": {"default": "Network"},
                        "Parameters": ["VpcId", "SubnetId"],
                    }
                ]
            },
            0,
        ),
        (
            "One parameter missing from ParameterGroups",
            {
                "ParameterGroups": [
                    {
                        "Label": {"default": "Network"},
                        "Parameters": ["VpcId"],
                    }
                ]
            },
            1,
        ),
        (
            "No ParameterGroups defined",
            {},
            2,
        ),
        (
            "Parameters spread across multiple groups",
            {
                "ParameterGroups": [
                    {"Label": {"default": "Group A"}, "Parameters": ["VpcId"]},
                    {"Label": {"default": "Group B"}, "Parameters": ["SubnetId"]},
                ]
            },
            0,
        ),
        (
            "Non-dict instance is skipped",
            "invalid",
            0,
        ),
        (
            "Non-dict entries in ParameterGroups are skipped",
            {
                "ParameterGroups": [
                    "not-a-dict",
                    {"Parameters": ["VpcId", "SubnetId"]},
                ]
            },
            0,
        ),
        (
            "Non-string entries in Parameters are skipped",
            {
                "ParameterGroups": [
                    {"Parameters": [{"Ref": "VpcId"}, "SubnetId"]},
                ]
            },
            1,
        ),
    ],
)
def test_validate(name, instance, expected_count, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert len(errs) == expected_count, (
        f"Test {name!r}: expected {expected_count} error(s), got {errs!r}"
    )
    for err in errs:
        assert isinstance(err, ValidationError)
        assert err.rule == rule
