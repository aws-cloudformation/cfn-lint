"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.rules.jsonschema.CfnLintRelationship import CfnLintRelationship


@pytest.fixture
def rule():
    return CfnLintRelationship(
        keywords=[], relationship="Resources/AWS::EC2::Instance/Properties/ImageId"
    )


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
        "Resources": {
            "One": {
                "Type": "AWS::EC2::Instance",
                "Properties": {
                    "ImageId": {
                        "Fn::If": [
                            "IsUsEast1",
                            {"Ref": "ImageId"},
                            {"Ref": "AWS::NoValue"},
                        ]
                    },
                },
            },
            "ParentOne": {
                "Type": "AWS::EC2::Instance",
                "Properties": {"ImageId": {"Fn::GetAtt": ["One", "ImageId"]}},
            },
            "Two": {
                "Type": "AWS::EC2::Instance",
                "Properties": {
                    "ImageId": {"Ref": "ImageId"},
                },
            },
            "ParentTwo": {
                "Type": "AWS::EC2::Instance",
                "Properties": {"ImageId": {"Fn::GetAtt": ["Two", "ImageId"]}},
            },
            "Three": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsUsEast1",
                "Properties": {
                    "ImageId": {
                        "Fn::If": [
                            "IsImageIdSpecified",
                            {"Ref": "ImageId"},
                            {"Ref": "AWS::NoValue"},
                        ],
                    },
                },
            },
            "ParentThree": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsImageIdSpecified",
                "Properties": {"ImageId": {"Fn::GetAtt": ["Three", "ImageId"]}},
            },
            "Four": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsUsEast1",
                "Properties": {
                    "ImageId": {
                        "Fn::If": [
                            "IsImageIdSpecified",
                            {"Ref": "ImageId"},
                            {"Ref": "AWS::NoValue"},
                        ]
                    },
                },
            },
            "ParentFour": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsImageIdSpecified",
                "Properties": {"ImageId": {"Fn::GetAtt": ["Four", "ImageId"]}},
            },
            "Five": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsUsEast1",
                "Properties": {
                    "ImageId": {
                        "Fn::If": [
                            "IsImageIdSpecified",
                            {"Ref": "ImageId"},
                        ]
                    },
                },
            },
            "ParentFive": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsImageIdSpecified",
                "Properties": {"ImageId": {"Fn::GetAtt": ["Five", "ImageId"]}},
            },
            "Six": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsUsEast1",
                "Properties": "Foo",
            },
            "ParentSix": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsImageIdSpecified",
                "Properties": {"ImageId": {"Fn::GetAtt": ["Six", "ImageId"]}},
            },
            "Seven": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsNotUsEast1",
                "Properties": {
                    "ImageId": {
                        "Fn::If": [
                            "IsImageIdSpecified",
                            {"Ref": "ImageId"},
                            {"Ref": "AWS::NoValue"},
                        ]
                    },
                },
            },
            "ParentSeven": {
                "Type": "AWS::EC2::Instance",
                "Condition": "IsUsEast1",
                "Properties": {"ImageId": {"Fn::GetAtt": ["Seven", "ImageId"]}},
            },
            "Eight": {
                "Properties": {
                    "ImageId": {
                        "Fn::If": [
                            "IsImageIdSpecified",
                            {"Ref": "ImageId"},
                            {"Ref": "AWS::NoValue"},
                        ]
                    },
                },
            },
            "ParentEight": {
                "Type": "AWS::EC2::Instance",
                "Properties": {"ImageId": {"Fn::GetAtt": ["Eight", "ImageId"]}},
            },
        },
    }


@pytest.mark.parametrize(
    "name,path,status,expected",
    [
        (
            "One",
            deque(["Resources", "ParentOne", "Properties", "ImageId"]),
            {},
            [
                ({"Ref": "ImageId"}, {"IsUsEast1": True}),
                (None, {"IsUsEast1": False}),
            ],
        ),
        (
            "Two",
            deque(["Resources", "ParentTwo", "Properties", "ImageId"]),
            {},
            [({"Ref": "ImageId"}, {})],
        ),
        (
            "Three",
            deque(["Resources", "ParentThree", "Properties", "ImageId"]),
            {
                "IsImageIdSpecified": True,
            },
            [({"Ref": "ImageId"}, {"IsUsEast1": True, "IsImageIdSpecified": True})],
        ),
        (
            "Four",
            deque(["Resources", "ParentFour", "Properties", "ImageId"]),
            {
                "IsImageIdSpecified": True,
            },
            [
                ({"Ref": "ImageId"}, {"IsUsEast1": True, "IsImageIdSpecified": True}),
            ],
        ),
        (
            "Five",
            deque(["Resources", "ParentFive", "Properties", "ImageId"]),
            {},
            [],
        ),
        (
            "Six",
            deque(["Resources", "ParentSix", "Properties", "ImageId"]),
            {},
            [],
        ),
        (
            "Seven",
            deque(["Resources", "ParentSeven", "Properties", "ImageId"]),
            {
                "IsUsEast1": True,
            },
            [()],
        ),
        (
            "Short Path",
            deque(["Resources"]),
            {},
            [],
        ),
        (
            "Not in resources",
            deque(["Outputs", "MyOutput"]),
            {},
            [],
        ),
        (
            "No type on relationshiop",
            deque(["Resources", "ParentEight", "Properties", "ImageId"]),
            {},
            [],
        ),
    ],
)
def test_get_relationships(name, path, status, expected, rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(path),
            conditions=validator.context.conditions.evolve(
                status=status,
            ),
        ),
    )
    results = list(rule.get_relationship(validator))
    assert len(results) == len(expected), f"Test {name!r} got {len(results)!r}"
    for result, exp in zip(results, expected):
        assert result[0] == exp[0], f"Test {name!r} got {result[0]!r}"
        assert (
            result[1].context.conditions.status == exp[1]
        ), f"Test {name!r} got {result[1].context.conditions.status!r}"
