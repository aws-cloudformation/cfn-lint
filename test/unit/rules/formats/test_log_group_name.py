"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json

import pytest

from cfnlint.api import lint
from cfnlint.rules.formats.LogGroupName import LogGroupName


@pytest.fixture(scope="module")
def rule():
    rule = LogGroupName()
    yield rule


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Valid log group name",
            "123457",
            True,
        ),
        (
            "Valid with invalid type",
            [],
            True,
        ),
        (
            "Valid log group name with special characters",
            "aws/one.two-three#four_five",
            True,
        ),
        ("Invalid log group name because of special character", "foo&bar", False),
        ("Invalid log group name because of empty", "", False),
        ("Invalid log group name because too long", "a" * 513, False),
    ],
)
def test_validate(name, instance, expected, rule, validator):
    result = rule.format(validator, instance)
    assert result == expected, f"Test {name!r} got {result!r}"


@pytest.mark.parametrize(
    "resource_type,properties,expected",
    [
        ("AWS::Logs::LogGroup", {"LogGroupName": "bad name with spaces"}, ["E1155"]),
        ("AWS::Logs::LogGroup", {"LogGroupName": "aws/one.two-three#four_five"}, []),
        (
            "AWS::EC2::SubnetRouteTableAssociation",
            {"RouteTableId": "rtb-0123456789abcdef0", "SubnetId": "subnet$bad"},
            ["E1154"],
        ),
    ],
)
def test_format_registration(resource_type, properties, expected):
    template = {
        "Resources": {"Resource": {"Type": resource_type, "Properties": properties}}
    }
    matches = lint(json.dumps(template), regions=["us-east-1"])
    assert (
        sorted(
            match.rule.id for match in matches if match.rule.id in ("E1154", "E1155")
        )
        == expected
    )
