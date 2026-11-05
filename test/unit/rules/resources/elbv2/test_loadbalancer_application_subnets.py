"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError

# ruff: noqa: E501
from cfnlint.rules.resources.elasticloadbalancingv2.LoadBalancerApplicationSubnets import (
    LoadBalancerApplicationSubnets,
)


@pytest.fixture(scope="module")
def rule():
    rule = LoadBalancerApplicationSubnets()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"Type": "network"},
            [],
        ),
        (
            {"Type": "application", "Subnets": ["SubnetA", "SubnetB"]},
            [],
        ),
        (
            {"Type": "network", "Subnets": ["SubnetA"]},
            [],
        ),
        (
            {"Subnets": ["SubnetA"]},
            [
                ValidationError(
                    "expected minimum item count: 2, found: 1",
                    rule=LoadBalancerApplicationSubnets(),
                    path=deque(["Subnets"]),
                    validator="minItems",
                    schema_path=deque(["then", "properties", "Subnets", "minItems"]),
                )
            ],
        ),
        (
            {
                "Type": "application",
                "Subnets": ["SubnetA"],
            },
            [
                ValidationError(
                    "expected minimum item count: 2, found: 1",
                    rule=LoadBalancerApplicationSubnets(),
                    path=deque(["Subnets"]),
                    validator="minItems",
                    schema_path=deque(["then", "properties", "Subnets", "minItems"]),
                )
            ],
        ),
    ],
)
def test_backup_lifecycle(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"


_template = {
    "Parameters": {
        "SubnetId": {"Type": "AWS::EC2::Subnet::Id"},
    },
    "Resources": {
        "LocalZoneSubnet": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "VpcId": "vpc-123",
                "CidrBlock": "10.0.0.0/24",
                "AvailabilityZone": "us-west-2-lax-1a",
            },
        },
        "ZoneSubnet": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "VpcId": "vpc-123",
                "CidrBlock": "10.0.1.0/24",
                "AvailabilityZone": "us-west-2a",
            },
        },
    },
}


@pytest.mark.parametrize(
    "instance,template,expected",
    [
        (
            {"Subnets": [{"Ref": "LocalZoneSubnet"}]},
            _template,
            [],
        ),
        (
            {"SubnetMappings": [{"SubnetId": {"Ref": "LocalZoneSubnet"}}]},
            _template,
            [],
        ),
        (
            {"Subnets": [{"Ref": "ZoneSubnet"}]},
            _template,
            [
                ValidationError(
                    "expected minimum item count: 2, found: 1",
                    rule=LoadBalancerApplicationSubnets(),
                    path=deque(["Subnets"]),
                    validator="minItems",
                    schema_path=deque(["then", "properties", "Subnets", "minItems"]),
                )
            ],
        ),
        (
            {"Subnets": [{"Ref": "SubnetId"}]},
            _template,
            [
                ValidationError(
                    "expected minimum item count: 2, found: 1",
                    rule=LoadBalancerApplicationSubnets(),
                    path=deque(["Subnets"]),
                    validator="minItems",
                    schema_path=deque(["then", "properties", "Subnets", "minItems"]),
                )
            ],
        ),
        (
            {"SubnetMappings": [{"SubnetId": {"Ref": "ZoneSubnet"}}]},
            _template,
            [
                ValidationError(
                    "expected minimum item count: 2, found: 1",
                    rule=LoadBalancerApplicationSubnets(),
                    path=deque(["SubnetMappings"]),
                    validator="minItems",
                    schema_path=deque(
                        ["then", "properties", "SubnetMappings", "minItems"]
                    ),
                )
            ],
        ),
    ],
    indirect=["template"],
)
def test_local_zone_subnets(instance, template, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert errs == expected, f"Expected {expected} got {errs}"
