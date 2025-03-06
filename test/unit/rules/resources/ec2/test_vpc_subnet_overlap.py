"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from ipaddress import ip_network

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.VpcSubnetOverlap import VpcSubnetOverlap


@pytest.fixture(scope="module")
def rule():
    rule = VpcSubnetOverlap()
    yield rule


@pytest.fixture
def template():
    return {
        "Parameters": {"MyCidr": {"Type": "String"}},
        "Conditions": {
            "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
            "IsUsWest2": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-west-2"]},
            "IsUs": {
                "Fn::Or": [
                    {"Condition": "IsUsEast1"},
                    {"Condition": "IsUsWest2"},
                ]
            },
            "IsNotUs": {"Fn::Not": [{"Condition": "IsUs"}]},
        },
        "Resources": {},
    }


@pytest.mark.parametrize(
    "name,instance,starting_subnets,expected",
    [
        (
            "Valid with no overlap on ipv4",
            {"VpcId": {"Ref": "Vpc"}, "CidrBlock": "10.0.1.0/24"},
            {"Vpc": [(ip_network("10.0.0.0/24"), {})]},
            [],
        ),
        (
            "Valid with a bad cidr",
            {"VpcId": {"Ref": "Vpc"}, "CidrBlock": "10.0.0/24"},
            {"Vpc": [(ip_network("10.0.0.0/24"), {})]},
            [],
        ),
        (
            "Valid with no overlap on ipv6",
            {"VpcId": {"Fn::GetAtt": "Vpc.VpcId"}, "Ipv6CidrBlock": "2001:db8::/32"},
            {"Vpc": [(ip_network("2002:db8::/32"), {})]},
            [],
        ),
        (
            "Valid with a function",
            {"VpcId": {"Ref": "Vpc"}, "CidrBlock": {"Ref": "MyCidr"}},
            {"Vpc": [(ip_network("10.0.0.0/24"), {})]},
            [],
        ),
        (
            "Valid with no previous setting",
            {"VpcId": "vpc-123456", "CidrBlock": "10.0.0.0/24"},
            {},
            [],
        ),
        (
            "Valid with an invalid function",
            {"VpcId": {"DNE": "Vpc"}, "CidrBlock": "10.0.0/24"},
            {"Vpc": [(ip_network("10.0.0.0/24"), {})]},
            [],
        ),
        (
            "Valid with vpc using another function",
            {"VpcId": {"Fn::Join": ["vpc-1"]}, "CidrBlock": "10.0.1.0/24"},
            {"Vpc": [(ip_network("10.0.0.0/24"), {})]},
            [],
        ),
        (
            "Invalid with a overlap on ipv4",
            {"VpcId": {"Ref": "Vpc"}, "CidrBlock": "10.0.0.0/24"},
            {"Vpc": [(ip_network("10.0.0.0/22"), {})]},
            [
                ValidationError(
                    "'10.0.0.0/24' overlaps with '10.0.0.0/22'",
                    rule=VpcSubnetOverlap(),
                    path=deque(["CidrBlock"]),
                )
            ],
        ),
        (
            "Invalid with a overlap on ipv6",
            {"VpcId": {"Ref": "Vpc"}, "Ipv6CidrBlock": "fc00::/32"},
            {"Vpc": [(ip_network("fc00::/16"), {})]},
            [
                ValidationError(
                    "'fc00::/32' overlaps with 'fc00::/16'",
                    rule=VpcSubnetOverlap(),
                    path=deque(["Ipv6CidrBlock"]),
                )
            ],
        ),
        (
            "Valid with ipv4 and ipv6",
            {"VpcId": {"Ref": "Vpc"}, "Ipv6CidrBlock": "fc01::/32"},
            {
                "Vpc": [
                    (ip_network("fc00::/32"), {}),
                    (ip_network("10.0.0.0/24"), {}),
                ]
            },
            [],
        ),
        (
            "Valid with conflicting conditions",
            {
                "VpcId": {"Ref": "Vpc"},
                "CidrBlock": {
                    "Fn::If": ["IsNotUs", "10.0.0.0/24", {"Ref": "AWS::NoValue"}]
                },
            },
            {
                "Vpc": [
                    (
                        ip_network("10.0.0.0/24"),
                        {
                            "IsUsEast1": True,
                            "IsUsWest2": False,
                            "IsUs": True,
                            "IsNotUs": False,
                        },
                    ),
                ]
            },
            [],
        ),
        (
            "Invalid with conflicting conditions",
            {
                "VpcId": {"Ref": "Vpc"},
                "CidrBlock": {"Fn::If": ["IsNotUs", "10.0.1.0/24", "10.0.0.0/32"]},
            },
            {
                "Vpc": [
                    (
                        ip_network("10.0.0.0/24"),
                        {
                            "IsUsEast1": True,
                            "IsUsWest2": False,
                            "IsUs": True,
                            "IsNotUs": False,
                        },
                    ),
                ]
            },
            [
                ValidationError(
                    "'10.0.0.0/32' overlaps with '10.0.0.0/24'",
                    rule=VpcSubnetOverlap(),
                    path=deque(["CidrBlock", "Fn::If", 2]),
                )
            ],
        ),
    ],
    indirect=[],
)
def test_validate(name, instance, starting_subnets, expected, rule, validator):

    rule._subnets = starting_subnets
    errs = list(rule.validate(validator, "", instance, {}))

    assert (
        errs == expected
    ), f"Expected test {name!r} to have {expected!r} but got {errs!r}"
