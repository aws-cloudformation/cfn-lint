"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.template import Template


@pytest.fixture
def cfn() -> Template:

    return Template(
        None,
        {
            "Parameters": {
                "Environment": {
                    "Type": "String",
                    "AllowedValues": ["dev", "test", "stage", "prod"],
                }
            },
            "Conditions": {
                "IsUsEast1": {"Fn::Equals": [{"Ref": "AWS::Region"}, "us-east-1"]},
                "IsProduction": {"Fn::Equals": [{"Ref": "Environment"}, "prod"]},
            },
            "Resources": {
                "Bucket": {"Type": "AWS::S3::Bucket", "Condition": "IsUsEast1"},
                "Vpc": {
                    "Type": "AWS::EC2::VPC",
                    "Properties": {"CidrBlock": "10.0.0.0/16"},
                },
                "SecurityGroup1": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Condition": "IsProduction",
                    "Properties": {
                        "CidrBlock": "10.0.0.0/24",
                        "VpcId": {
                            "Fn::If": ["IsUsEast1", "vpc-123", {"Ref": "AWS::NoValue"}]
                        },
                    },
                },
                "SecurityGroup2": {
                    "Type": "AWS::EC2::SecurityGroup",
                    "Condition": "IsProduction",
                    "Properties": {
                        "CidrBlock": "10.0.1.0/24",
                        "VpcId": {
                            "Fn::If": ["IsProduction", {"Ref": "Vpc"}, "vpc-abc"]
                        },
                    },
                },
            },
        },
    )


@pytest.mark.parametrize(
    "name,path,starting_conditions, expected",
    [
        (
            "Valid get path",
            ["Resources", "Vpc", "Properties", "CidrBlock"],
            {},
            [("10.0.0.0/16", {})],
        ),
        (
            "Invalid path returns nothing",
            ["Resources", "Vpc", "Properties", "DNE"],
            {},
            [],
        ),
        (
            "Short path that doesn't exist",
            ["Resources", "DNE"],
            {},
            [],
        ),
        (
            "Valid path with resource condition",
            ["Resources", "SecurityGroup1", "Properties", "CidrBlock"],
            {},
            [("10.0.0.0/24", {"IsProduction": True})],
        ),
        (
            "Valid path with resource condition",
            ["Resources", "SecurityGroup1", "Properties", "CidrBlock"],
            {"IsProduction": False},
            [],
        ),
        (
            "Valid path with resource condition with multiple conditions",
            ["Resources", "SecurityGroup1", "Properties", "VpcId"],
            {},
            [("vpc-123", {"IsProduction": True, "IsUsEast1": True})],
        ),
        (
            (
                "Valid path with resource condition with multiple "
                "conditions that conflict with each other"
            ),
            ["Resources", "SecurityGroup2", "Properties", "VpcId"],
            {},
            [({"Ref": "Vpc"}, {"IsProduction": True})],
        ),
    ],
)
def test_paths(name, path, starting_conditions, expected, cfn):

    context = cfn.context.evolve(
        conditions=cfn.context.conditions.evolve(starting_conditions)
    )

    results = list(cfn.get_cfn_path(path, context))

    assert len(results) == len(
        expected
    ), f"{name!r} test failed. Got results {results!r}"

    for i, value in enumerate(results):
        assert (
            value[0] == expected[i][0]
        ), f"{name!r} test failed for {i}. Got value {value[0]!r}"
        assert value[1].conditions.status == expected[i][1], (
            f"{name!r} test failed for {i}. Got "
            f"conditions {value[1].conditions.status[0]!r}"
        )
