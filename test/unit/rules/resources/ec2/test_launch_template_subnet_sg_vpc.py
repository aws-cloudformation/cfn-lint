"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.resources.ectwo.LaunchTemplateSubnetSecurityGroupVpc import (
    LaunchTemplateSubnetSecurityGroupVpc,
)


@pytest.fixture(scope="module")
def rule():
    return LaunchTemplateSubnetSecurityGroupVpc()


_template = {
    "Resources": {
        "Vpc": {
            "Type": "AWS::EC2::VPC",
            "Properties": {"CidrBlock": "10.0.0.0/16"},
        },
        "Subnet1": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "VpcId": {"Ref": "Vpc"},
                "CidrBlock": "10.0.1.0/24",
            },
        },
        "SG1": {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "SG1",
                "VpcId": {"Ref": "Vpc"},
            },
        },
        "LaunchTemplate": {
            "Type": "AWS::EC2::LaunchTemplate",
            "Properties": {
                "LaunchTemplateData": {
                    "SecurityGroupIds": [{"Ref": "SG1"}],
                    "NetworkInterfaces": [
                        {
                            "DeviceIndex": 0,
                            "SubnetId": {"Ref": "Subnet1"},
                            "Groups": [{"Ref": "SG1"}],
                        }
                    ],
                },
            },
        },
    },
}


@pytest.mark.parametrize(
    "template,start_path,expected",
    [
        # Same VPC — valid
        (
            _template,
            deque(["Resources", "LaunchTemplate", "Properties"]),
            [],
        ),
        # Different VPCs — invalid
        (
            {
                "Resources": {
                    "Vpc1": {
                        "Type": "AWS::EC2::VPC",
                        "Properties": {"CidrBlock": "10.0.0.0/16"},
                    },
                    "Vpc2": {
                        "Type": "AWS::EC2::VPC",
                        "Properties": {"CidrBlock": "10.1.0.0/16"},
                    },
                    "Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "VpcId": {"Ref": "Vpc1"},
                            "CidrBlock": "10.0.1.0/24",
                        },
                    },
                    "SG1": {
                        "Type": "AWS::EC2::SecurityGroup",
                        "Properties": {
                            "GroupDescription": "SG1",
                            "VpcId": {"Ref": "Vpc2"},
                        },
                    },
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateData": {
                                "SecurityGroupIds": [{"Ref": "SG1"}],
                                "NetworkInterfaces": [
                                    {
                                        "DeviceIndex": 0,
                                        "SubnetId": {"Ref": "Subnet1"},
                                    }
                                ],
                            },
                        },
                    },
                },
            },
            deque(["Resources", "LaunchTemplate", "Properties"]),
            [
                ValidationError(
                    (
                        "SecurityGroup VpcId does not match Subnet VpcId "
                        "in the LaunchTemplate"
                    ),
                    validator="const",
                    rule=LaunchTemplateSubnetSecurityGroupVpc(),
                    path=deque([]),
                    schema_path=deque(
                        [
                            "cfnGather",
                            "schema",
                            "cfnContext",
                            "schema",
                            "then",
                            "properties",
                            "securityGroup",
                            "properties",
                            "VpcId",
                            "const",
                        ]
                    ),
                    path_override=deque(
                        [
                            "Resources",
                            "SG1",
                            "Properties",
                            "VpcId",
                        ]
                    ),
                ),
            ],
        ),
        # No NetworkInterfaces — valid (no subnet to compare)
        (
            {
                "Resources": {
                    "SG1": {
                        "Type": "AWS::EC2::SecurityGroup",
                        "Properties": {
                            "GroupDescription": "SG1",
                            "VpcId": {"Ref": "Vpc"},
                        },
                    },
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateData": {
                                "SecurityGroupIds": [{"Ref": "SG1"}],
                            },
                        },
                    },
                },
            },
            deque(["Resources", "LaunchTemplate", "Properties"]),
            [],
        ),
        # No SecurityGroupIds — valid (no SG to compare)
        (
            {
                "Resources": {
                    "Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "VpcId": {"Ref": "Vpc"},
                            "CidrBlock": "10.0.1.0/24",
                        },
                    },
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateData": {
                                "NetworkInterfaces": [
                                    {
                                        "DeviceIndex": 0,
                                        "SubnetId": {"Ref": "Subnet1"},
                                    }
                                ],
                            },
                        },
                    },
                },
            },
            deque(["Resources", "LaunchTemplate", "Properties"]),
            [],
        ),
        # Hardcoded SecurityGroupId string — valid (no Ref to follow)
        (
            {
                "Resources": {
                    "Subnet1": {
                        "Type": "AWS::EC2::Subnet",
                        "Properties": {
                            "VpcId": {"Ref": "Vpc"},
                            "CidrBlock": "10.0.1.0/24",
                        },
                    },
                    "LaunchTemplate": {
                        "Type": "AWS::EC2::LaunchTemplate",
                        "Properties": {
                            "LaunchTemplateData": {
                                "SecurityGroupIds": ["sg-12345678"],
                                "NetworkInterfaces": [
                                    {
                                        "DeviceIndex": 0,
                                        "SubnetId": {"Ref": "Subnet1"},
                                    }
                                ],
                            },
                        },
                    },
                },
            },
            deque(["Resources", "LaunchTemplate", "Properties"]),
            [],
        ),
    ],
    indirect=["template"],
)
def test_validate(template, start_path, expected, rule, validator):
    for instance, instance_validator in get_value_from_path(
        validator, template, start_path
    ):
        errs = list(rule.validate(instance_validator, "", instance, {}))
        assert errs == expected, f"Expected {expected} got {errs}"
