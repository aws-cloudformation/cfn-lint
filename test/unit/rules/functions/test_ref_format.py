"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.RefFormat import RefFormat


@pytest.fixture(scope="module")
def rule():
    rule = RefFormat()
    yield rule


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyBucket": {"Type": "AWS::S3::Bucket"},
            "MyVpc": {"Type": "AWS::EC2::VPC"},
            "MySecurityGroup": {"Type": "AWS::EC2::SecurityGroup"},
            "MyCustomResource": {"Type": "Custom::CustomResource"},
            "MySubTemplate": {"Type": "AWS::CloudFormation::Stack"},
            "MyProvisionedProduct": {
                "Type": "AWS::ServiceCatalog::CloudFormationProvisionedProduct"
            },
            "MySSMParameter": {"Type": "AWS::SSM::Parameter"},
        },
    }


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Ref with a good format",
            {"Ref": "MyVpc"},
            {"format": "AWS::EC2::VPC.Id"},
            [],
        ),
        (
            "Invalid Ref with a bad format",
            {"Ref": "MyVpc"},
            {"format": "AWS::EC2::Image.Id"},
            [
                ValidationError(
                    (
                        "{'Ref': 'MyVpc'} with format "
                        "'AWS::EC2::VPC.Id' does not match "
                        "destination format of 'AWS::EC2::Image.Id'"
                    ),
                    rule=RefFormat(),
                )
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.validate(validator, schema, instance, schema))
    assert errs == expected, f"Test {name!r} got {errs!r}"
