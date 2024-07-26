"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.rules.helpers import get_resource_by_name


@pytest.fixture
def template():
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Parameters": {
            "ImageId": {
                "Type": "String",
            }
        },
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsNotUsEast1": {"Fn::Not": [{"Condition": "IsUsEast1"}]},
            "IsImageId": {"Fn::Not": {"Fn::Equals": [{"Ref": "ImageId"}, ""]}},
        },
        "Resources": {
            "Foo": {"Type": "AWS::S3::Bucket"},
            "Bar": {"Type": "AWS::S3::Bucket", "Condition": "IsUsEast1"},
            "FooBar": {"Type": "AWS::S3::Bucket", "Condition": "IsNotUsEast1"},
            "BadShape": [],
            "NoType": {},
        },
    }


@pytest.mark.parametrize(
    "name,resource_name,types,status,expected",
    [
        (
            "Standard get",
            "Foo",
            None,
            {},
            ({"Type": "AWS::S3::Bucket"}, {}, deque(["Resources", "Foo"])),
        ),
        (
            "Doesn't exist",
            "Foo2",
            None,
            {},
            (
                None,
                {},
                deque([]),
            ),
        ),
        (
            "The destination isn't a dict",
            "BadShape",
            None,
            {},
            (
                None,
                {},
                deque([]),
            ),
        ),
        (
            "The destination doesn't have type",
            "NoType",
            None,
            {},
            (
                None,
                {},
                deque([]),
            ),
        ),
        (
            "Get a valid resource with a filter",
            "Foo",
            ["AWS::S3::Bucket"],
            {},
            (
                {
                    "Type": "AWS::S3::Bucket",
                },
                {},
                deque(["Resources", "Foo"]),
            ),
        ),
        (
            "No result when type filters it out",
            "Foo",
            ["AWS::EC2::Instance"],
            {},
            (
                None,
                {},
                deque([]),
            ),
        ),
        (
            "Get a resource with a condition",
            "Bar",
            None,
            {},
            (
                {"Type": "AWS::S3::Bucket", "Condition": "IsUsEast1"},
                {"IsUsEast1": True},
                deque(["Resources", "Bar"]),
            ),
        ),
        (
            "No resource when conditions don't align 1",
            "Bar",
            None,
            {"IsUsEast1": False},
            (
                None,
                {"IsUsEast1": False},
                deque([]),
            ),
        ),
        (
            "No resource when conditions don't align 2",
            "FooBar",
            None,
            {"IsUsEast1": True},
            (
                None,
                {"IsUsEast1": True},
                deque([]),
            ),
        ),
        (
            "Unrelated conditions return full results",
            "Bar",
            None,
            {"IsImageId": False},
            (
                {"Type": "AWS::S3::Bucket", "Condition": "IsUsEast1"},
                {"IsUsEast1": True, "IsImageId": False},
                deque(["Resources", "Bar"]),
            ),
        ),
    ],
)
def test_get_resource_by_name(name, resource_name, types, status, expected, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            conditions=validator.context.conditions.evolve(
                status=status,
            ),
        ),
    )

    result = get_resource_by_name(validator, resource_name, types)

    assert result[0] == expected[0], f"Test {name!r} got {result[0]!r}"
    assert (
        result[1].context.conditions.status == expected[1]
    ), f"Test {name!r} got {result[1].context.conditions.status!r}"
    assert (
        result[1].context.path.path == expected[2]
    ), f"Test {name!r} got {result[1].context.path.path!r}"
