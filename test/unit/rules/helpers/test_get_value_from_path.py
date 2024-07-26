"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.rules.helpers import get_value_from_path


@pytest.fixture
def template():
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Parameters": {
            "ImageId": {
                "Type": "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
                "Default": "/aws/service/ami-amazon-linux-latest/amzn-ami-hvm-x86_64-gp2",  # noqa: E501
            }
        },
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsNotUsEast1": {"Fn::Not": [{"Condition": "IsUsEast1"}]},
            "IsImageIdSpecified": {
                "Fn::Not": [{"Fn::Equals": [{"Ref": "ImageId"}, ""]}]
            },
        },
        "Resources": {},
    }


@pytest.mark.parametrize(
    "name,instance,v_path,status,expected",
    [
        (
            "No path",
            {"Foo": "Bar"},
            deque([]),
            {},
            [
                ({"Foo": "Bar"}, {}, deque([])),
            ],
        ),
        (
            "Small path with out it being found",
            {"Foo": "Bar"},
            deque(["Bar"]),
            {},
            [
                (None, {}, deque(["Bar"])),
            ],
        ),
        (
            "Bad path returns an empty value with list",
            {"Foo": [{"Bar": "One"}]},
            deque(["Foo", "Bar"]),
            {},
            [
                (
                    None,
                    {},
                    deque(["Foo"]),
                )
            ],
        ),
        (
            "Bad path returns an empty value with string",
            {"Foo": "Misvalued"},
            deque(["Foo", "Bar"]),
            {},
            [
                (
                    None,
                    {},
                    deque(["Foo"]),
                )
            ],
        ),
        (
            "With a path and no conditions",
            {"Foo": {"Bar": True}},
            deque(["Foo", "Bar"]),
            {},
            [
                (True, {}, deque(["Foo", "Bar"])),
            ],
        ),
        (
            "With a list item",
            {"Foo": [{"Bar": "One"}, {"Bar": "Two"}, {"NoValue": "Three"}]},
            deque(["Foo", "*", "Bar"]),
            {},
            [
                ("One", {}, deque(["Foo", 0, "Bar"])),
                ("Two", {}, deque(["Foo", 1, "Bar"])),
                (None, {}, deque(["Foo", 2, "Bar"])),
            ],
        ),
        (
            "With a basic condition",
            {
                "Foo": {
                    "Fn::If": [
                        "IsUsEast1",
                        {"Bar": "One"},
                        {"Bar": "Two"},
                    ]
                }
            },
            deque(["Foo", "Bar"]),
            {},
            [
                ("One", {"IsUsEast1": True}, deque(["Foo", "Fn::If", 1, "Bar"])),
                ("Two", {"IsUsEast1": False}, deque(["Foo", "Fn::If", 2, "Bar"])),
            ],
        ),
        (
            "With a basic condition and a current status",
            {
                "Foo": {
                    "Fn::If": [
                        "IsUsEast1",
                        {"Bar": "One"},
                        {"Bar": "Two"},
                    ]
                }
            },
            deque(["Foo", "Bar"]),
            {"IsUsEast1": True},
            [
                ("One", {"IsUsEast1": True}, deque(["Foo", "Fn::If", 1, "Bar"])),
            ],
        ),
        (
            "With a basic condition and a current status on a related condition",
            {
                "Foo": {
                    "Fn::If": [
                        "IsUsEast1",
                        {"Bar": "One"},
                        {"Bar": "Two"},
                    ]
                }
            },
            deque(["Foo", "Bar"]),
            {"IsNotUsEast1": True},
            [
                (
                    "Two",
                    {"IsUsEast1": False, "IsNotUsEast1": True},
                    deque(["Foo", "Fn::If", 2, "Bar"]),
                ),
            ],
        ),
        (
            "With a random function in the way",
            {"Foo": {"Fn::FindInMap": ["A", "B", "C"]}},
            deque(["Foo", "*", "Bar"]),
            {},
            [],
        ),
        (
            "With a ref at the desination",
            {"Foo": {"Ref": "Bar"}},
            deque(["Foo"]),
            {},
            [({"Ref": "Bar"}, {}, deque(["Foo"]))],
        ),
    ],
)
def test_get_value_from_path(name, instance, v_path, status, expected, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            conditions=validator.context.conditions.evolve(
                status=status,
            ),
        ),
    )

    results = list(get_value_from_path(validator, instance, v_path))

    assert len(results) == len(expected), f"Test {name!r} got {len(results)!r}"
    for result, exp in zip(results, expected):
        assert result[0] == exp[0], f"Test {name!r} got {result[0]!r}"
        assert (
            result[1].context.conditions.status == exp[1]
        ), f"Test {name!r} got {result[1].context.conditions.status!r}"
        assert (
            result[1].context.path.path == exp[2]
        ), f"Test {name!r} got {result[1].context.path.path!r}"
