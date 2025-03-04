"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.VpcSubnetCidr import VpcSubnetCidr


@pytest.fixture(scope="module")
def rule():
    rule = VpcSubnetCidr()
    yield rule


_template = {
    "Resources": {
        "Vpc": {
            "Type": "AWS::EC2::VPC",
        },
        "VpcV4Subnet1": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "CidrBlock": "10.0.0.0/24",
                "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
            },
        },
        "SecurityGroupIngress": {
            "Type": "AWS::EC2::SecurityGroupIngress",
            "Properties": {
                "VpcId": {"Fn::GetAtt": ["Vpc", "DefaultSecurityGroup"]},
            },
        },
    }
}


@pytest.mark.parametrize(
    "name,instance,template,path,expected",
    [
        (
            "Valid with no Private Ip Address",
            {
                "CidrBlock": "10.0.0.0/16",
            },
            _template,
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Valid with bad ip address on VPC",
            {
                "CidrBlock": "10.0.0/16",
            },
            _template,
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Valid with a bad subnet IP Address",
            {
                "CidrBlock": "10.0.0.0/16",
            },
            {
                "Parameters": {"VpcCidr": {"Type": "String"}},
                "Resources": {
                    "Vpc": {
                        "Type": "AWS::EC2::VPC",
                    },
                    "VpcV4Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "CidrBlock": "10.0.0/24",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                },
            },
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Parameter CIDR",
            {
                "CidrBlock": {"Ref": "VpcCidr"},
            },
            {
                "Parameters": {"VpcCidr": {"Type": "String"}},
                "Resources": {
                    "Vpc": {
                        "Type": "AWS::EC2::VPC",
                    },
                    "VpcV4Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "CidrBlock": "10.0.0.0/24",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                },
            },
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Empty CidrBlocks should continue",
            {},
            _template,
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Subnet outside of the VPC",
            {
                "CidrBlock": "11.0.0.0/16",
            },
            _template,
            {"path": ["Resources", "Vpc", "Properties"]},
            [
                ValidationError(
                    "'10.0.0.0/24' is not a valid subnet of ['11.0.0.0/16']",
                    rule=VpcSubnetCidr(),
                    path_override=deque(
                        ["Resources", "VpcV4Subnet1", "Properties", "CidrBlock"]
                    ),
                )
            ],
        ),
        (
            "Subnet larger than VPC",
            {
                "CidrBlock": "10.0.0.0/32",
            },
            _template,
            {"path": ["Resources", "Vpc", "Properties"]},
            [
                ValidationError(
                    "'10.0.0.0/24' is not a valid subnet of ['10.0.0.0/32']",
                    rule=VpcSubnetCidr(),
                    path_override=deque(
                        ["Resources", "VpcV4Subnet1", "Properties", "CidrBlock"]
                    ),
                )
            ],
        ),
        (
            "Subnet IPV6 CIDR with no ipv6 allocations",
            {
                "CidrBlock": "11.0.0.0/16",
            },
            {
                "Resources": {
                    "Vpc": {
                        "Type": "AWS::EC2::VPC",
                    },
                    "VpcV4Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "Ipv6CidrBlock": "2001:db8::/32",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                },
            },
            {"path": ["Resources", "Vpc", "Properties"]},
            [
                ValidationError(
                    (
                        "'2001:db8::/32' is specified on a VPC that "
                        "has no ipv6 networks defined"
                    ),
                    rule=VpcSubnetCidr(),
                    path_override=deque(
                        ["Resources", "VpcV4Subnet1", "Properties", "Ipv6CidrBlock"]
                    ),
                )
            ],
        ),
        (
            "Subnet IPV6 CIDR valid with addtional block",
            {"CidrBlock": "10.0.0.0/16"},
            {
                "Resources": {
                    "Vpc": {
                        "Type": "AWS::EC2::VPC",
                    },
                    "VpcCidr": {
                        "Type": "AWS::EC2::VPCCidrBlock",
                        "Properties": {
                            "Ipv6CidrBlock": "fc00::/7",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                    "VpcV4Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "Ipv6CidrBlock": "fc00::/16",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                },
            },
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Invalid subnet IPV6 CIDR valid with addtional block",
            {"CidrBlock": "10.0.0.0/32"},
            {
                "Resources": {
                    "Vpc": {
                        "Type": "AWS::EC2::VPC",
                    },
                    "VpcCidr": {
                        "Type": "AWS::EC2::VPCCidrBlock",
                        "Properties": {
                            "Ipv6CidrBlock": "fc00::/32",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                    "VpcV4Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "Ipv6CidrBlock": "fc00::/16",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                },
            },
            {"path": ["Resources", "Vpc", "Properties"]},
            [
                ValidationError(
                    "'fc00::/16' is not a valid subnet of ['fc00::/32']",
                    rule=VpcSubnetCidr(),
                    path_override=deque(
                        ["Resources", "VpcV4Subnet1", "Properties", "Ipv6CidrBlock"]
                    ),
                )
            ],
        ),
        (
            "Subnet IPV4 CIDR valid with IPam Pool ID",
            {"Ipv4IpamPoolId": "poolid"},
            _template,
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Subnet IPV4 CIDR valid with multiple CIDRs",
            {"CidrBlock": "10.0.0.0/16"},
            {
                "Resources": {
                    "Vpc": {
                        "Type": "AWS::EC2::VPC",
                    },
                    "VpcCidr": {
                        "Type": "AWS::EC2::VPCCidrBlock",
                        "Properties": {
                            "CidrBlock": "11.0.0.0/16",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                    "VpcV4Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "CidrBlock": "11.0.0.0/24",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                },
            },
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Subnet IPV4 CIDR invalid with multiple CIDRs with ipam pool ID",
            {"CidrBlock": "10.0.0.0/16"},
            {
                "Resources": {
                    "Vpc": {
                        "Type": "AWS::EC2::VPC",
                    },
                    "VpcCidr": {
                        "Type": "AWS::EC2::VPCCidrBlock",
                        "Properties": {
                            "Ipv4IpamPoolId": "pool-id",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                    "VpcV4Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "CidrBlock": "11.0.0.0/16",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                },
            },
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
        (
            "Subnet IPV6 CIDR invalid with multiple CIDRs and one ipam pool ID",
            {"CidrBlock": "10.0.0.0/16"},
            {
                "Resources": {
                    "Vpc": {
                        "Type": "AWS::EC2::VPC",
                    },
                    "VpcCidr1": {
                        "Type": "AWS::EC2::VPCCidrBlock",
                        "Properties": {
                            "Ipv6IpamPoolId": "pool-id",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                    "VpcCidr2": {
                        "Type": "AWS::EC2::VPCCidrBlock",
                        "Properties": {
                            "Ipv6CidrBlock": "fc00::/32",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                    "VpcV4Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "Ipv6CidrBlock": "fc00::/16",
                            "VpcId": {"Fn::GetAtt": ["Vpc", "VpcId"]},
                        },
                    },
                },
            },
            {"path": ["Resources", "Vpc", "Properties"]},
            [],
        ),
    ],
    indirect=["template", "path"],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert (
        errs == expected
    ), f"Expected test {name!r} to have {expected!r} but got {errs!r}"
