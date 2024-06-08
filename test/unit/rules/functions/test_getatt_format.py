"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.GetAttFormat import GetAttFormat


@pytest.fixture(scope="module")
def rule():
    rule = GetAttFormat()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyBucket": {"Type": "AWS::S3::Bucket"},
            "MyVpc": {"Type": "AWS::EC2::VPC"},
            "MySecurityGroup": {"Type": "AWS::EC2::SecurityGroup"},
        },
    }


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid GetAtt with a good format",
            ["MyVpc", "VpcId"],
            {"format": "AWS::EC2::VPC.Id"},
            [],
        ),
        (
            "Valid GetAtt because of exception",
            ["MyBucket", "Arn"],
            {"format": "AWS::EC2::SecurityGroup.GroupId"},
            [],
        ),
        (
            "Invalid GetAtt with a bad format",
            ["MyBucket", "Arn"],
            {"format": "AWS::EC2::VPC.Id"},
            [
                ValidationError(
                    (
                        "{'Fn::GetAtt': ['MyBucket', 'Arn']} that "
                        "does not match 'AWS::EC2::VPC.Id'"
                    ),
                    rule=GetAttFormat(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.validate(validator, schema, instance, schema))
    assert errs == expected, f"Test {name!r} got {errs!r}"
